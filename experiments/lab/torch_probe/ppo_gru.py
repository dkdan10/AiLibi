"""FROZEN (Phase 19 tier map, training/README.md): the torch probe, a clean negative.
Bug fixes and evidence readers only; no new search.

The torch side of the 15.17 probe: a PPO + GRU impostor learner.

Everything torch lives here and in the operator scripts — ``entrant.py`` (the
comparability plumbing the committed test drives) never imports this module.
Run via ``uv run --with torch`` (see the README); torch never enters
``pyproject.toml`` or ``uv.lock``.

Architecture (the probe question is RECURRENCE, so the head vocabulary is
kept deliberately identical to the 15.15 ``MaskedMlpPolicy`` family):

    encoder-v2 features (111) -> Linear -> tanh -> GRU (hidden) ->
        policy head (17 = 10 room slots + 7 kind slots)  +  value head (1)

Action selection scores each submission-legal candidate as the SUM of its
head-slot logits (``entrant.ScoredCandidate.slots`` — the same recipe the
frozen eval path and the pure-Python family use, including the vent-room
addition), then samples from the softmax over CANDIDATES during training and
takes the canonical-tie-break argmax when frozen.

PPO is the standard clipped objective with GAE over per-decision rewards (the
potential-shaped impostor series ``entrant.per_decision_rewards`` emits),
full-sequence BPTT from a zero initial hidden per trajectory (one trajectory
per impostor per episode; 9p2i episodes are short, ~30-60 decisions). The
15.15 anchor discipline enters as a piKL-style AUXILIARY loss — the
cross-entropy of the candidate softmax at the FSM's proposal, when on-menu —
rather than a reward term; the harness still charges the eval-time anchor CE
against the shared inner fitness identically for every entrant, so
comparability is preserved (the report documents this deviation).

Everything runs float64 on CPU with ``torch.set_num_threads(1)``:
single-threaded float64 keeps the frozen forward pass as reproducible as
torch gets, so the determinism-harness verdict measures torch's story, not
thread count.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LAB_ROOT = Path(__file__).resolve().parents[1]
for _path in (str(_REPO_ROOT), str(_LAB_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from collections.abc import Mapping, Sequence  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402

import torch  # noqa: E402
from torch import nn  # noqa: E402

from torch_probe.entrant import ScoredCandidate  # noqa: E402

torch.set_num_threads(1)

_DTYPE = torch.float64


@dataclass
class PpoConfig:
    """The PPO budget + hyperparameters (recorded verbatim in the report)."""

    input_dim: int
    head: int
    hidden: int = 64
    learning_rate: float = 3e-4
    gamma: float = 1.0
    gae_lambda: float = 0.95
    clip_ratio: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    anchor_coef: float = 0.3
    epochs_per_update: int = 4
    max_grad_norm: float = 0.5
    torch_seed: int = 0

    def as_config(self) -> dict[str, object]:
        return {
            "input_dim": self.input_dim,
            "head": self.head,
            "hidden": self.hidden,
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "gae_lambda": self.gae_lambda,
            "clip_ratio": self.clip_ratio,
            "value_coef": self.value_coef,
            "entropy_coef": self.entropy_coef,
            "anchor_coef": self.anchor_coef,
            "epochs_per_update": self.epochs_per_update,
            "max_grad_norm": self.max_grad_norm,
            "torch_seed": self.torch_seed,
        }


class GruPolicyValueNet(nn.Module):
    """Feature MLP -> GRU -> (policy head over 15.15 slots, value head)."""

    def __init__(self, *, input_dim: int, hidden: int, head: int) -> None:
        super().__init__()
        self.input_fc = nn.Linear(input_dim, hidden)
        self.gru = nn.GRU(hidden, hidden)
        self.policy_head = nn.Linear(hidden, head)
        self.value_head = nn.Linear(hidden, 1)

    def forward_sequence(
        self, features: torch.Tensor, hidden: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Run a [T, input_dim] feature sequence; returns (logits, values, h_T)."""

        x = torch.tanh(self.input_fc(features))
        out, h_final = self.gru(x.unsqueeze(1), hidden)
        out = out.squeeze(1)
        return self.policy_head(out), self.value_head(out).squeeze(-1), h_final


def _candidate_scores(
    logits: torch.Tensor, recipes: Sequence[tuple[int, ...]]
) -> torch.Tensor:
    """Score candidates as the sum of their head-slot logits (the 15.15 recipe)."""

    return torch.stack([logits[list(slots)].sum() for slots in recipes])


@dataclass
class _Step:
    features: tuple[float, ...]
    recipes: tuple[tuple[int, ...], ...]
    action: int
    fsm_index: int | None
    log_prob: float
    value: float


@dataclass
class _Trajectory:
    agent_id: str
    steps: list[_Step] = field(default_factory=list)
    rewards: list[float] = field(default_factory=list)


def flat_parameters(net: nn.Module) -> tuple[float, ...]:
    """Every parameter flattened in registration order (the frozen genome)."""

    values: list[float] = []
    for parameter in net.parameters():
        values.extend(
            float(v) for v in parameter.detach().to(_DTYPE).reshape(-1).tolist()
        )
    return tuple(values)


def load_flat_parameters(net: nn.Module, weights: Sequence[float]) -> None:
    """Refill a net from a flat genome (registration order, fail-loud length)."""

    cursor = 0
    with torch.no_grad():
        for parameter in net.parameters():
            count = parameter.numel()
            chunk = torch.tensor(
                list(weights[cursor : cursor + count]), dtype=_DTYPE
            ).reshape(parameter.shape)
            parameter.copy_(chunk)
            cursor += count
    if cursor != len(weights):
        raise ValueError(
            f"flat genome length {len(weights)} != parameter count {cursor}"
        )


def build_net_from_config(config: Mapping[str, object]) -> GruPolicyValueNet:
    """Rebuild the exact net from a frozen candidate's ``config.json``."""

    learner = config["learner"] if "learner" in config else config
    assert isinstance(learner, Mapping)
    net = GruPolicyValueNet(
        input_dim=int(learner["input_dim"]),  # type: ignore[call-overload]
        hidden=int(learner["hidden"]),  # type: ignore[call-overload]
        head=int(learner["head"]),  # type: ignore[call-overload]
    ).to(_DTYPE)
    return net


class FrozenGruScorer:
    """The frozen ``RecurrentScorer``: eval-mode net + per-agent hidden state."""

    def __init__(self, net: GruPolicyValueNet) -> None:
        self._net = net.to(_DTYPE)
        self._net.eval()
        self._hidden: dict[str, torch.Tensor] = {}

    def score(
        self, agent_id: str, features: Sequence[float], *, new_episode: bool
    ) -> Sequence[float]:
        if new_episode:
            self._hidden.pop(agent_id, None)
        hidden = self._hidden.get(agent_id)
        with torch.no_grad():
            x = torch.tensor([list(features)], dtype=_DTYPE)
            logits, _, h_final = self._net.forward_sequence(x, hidden)
        self._hidden[agent_id] = h_final
        return [float(v) for v in logits[0].tolist()]


class PpoGruLearner:
    """The ``ProbeLearner`` implementation the operator scripts train with."""

    def __init__(self, config: PpoConfig) -> None:
        self._config = config
        torch.manual_seed(config.torch_seed)
        self._net = GruPolicyValueNet(
            input_dim=config.input_dim, hidden=config.hidden, head=config.head
        ).to(_DTYPE)
        self._optimizer = torch.optim.Adam(
            self._net.parameters(), lr=config.learning_rate
        )
        self._generator = torch.Generator().manual_seed(config.torch_seed)
        self._hidden: dict[str, torch.Tensor] = {}
        self._open: dict[str, _Trajectory] = {}
        self._buffer: list[_Trajectory] = []
        self._updates_done = 0

    # ---- the ProbeLearner seam ------------------------------------------- #

    def act(
        self,
        agent_id: str,
        features: Sequence[float],
        candidates: Sequence[ScoredCandidate],
        *,
        fsm_index: int | None,
        new_episode: bool,
    ) -> int:
        if new_episode:
            self._hidden.pop(agent_id, None)
        hidden = self._hidden.get(agent_id)
        with torch.no_grad():
            x = torch.tensor([list(features)], dtype=_DTYPE)
            logits, values, h_final = self._net.forward_sequence(x, hidden)
        self._hidden[agent_id] = h_final
        recipes = tuple(item.slots for item in candidates)
        scores = _candidate_scores(logits[0], recipes)
        probabilities = torch.softmax(scores, dim=0)
        action = int(
            torch.multinomial(probabilities, 1, generator=self._generator).item()
        )
        log_prob = float(torch.log_softmax(scores, dim=0)[action].item())
        trajectory = self._open.setdefault(agent_id, _Trajectory(agent_id=agent_id))
        trajectory.steps.append(
            _Step(
                features=tuple(float(v) for v in features),
                recipes=recipes,
                action=action,
                fsm_index=fsm_index,
                log_prob=log_prob,
                value=float(values[0].item()),
            )
        )
        return action

    def episode_result(
        self, rewards_by_agent: Mapping[str, Sequence[float]], *, truncated: bool
    ) -> None:
        for agent_id, trajectory in self._open.items():
            rewards = list(rewards_by_agent.get(agent_id, ()))
            if len(rewards) != len(trajectory.steps):
                raise ValueError(
                    f"agent {agent_id!r}: {len(rewards)} rewards for "
                    f"{len(trajectory.steps)} decisions"
                )
            trajectory.rewards = rewards
            self._buffer.append(trajectory)
        self._open = {}
        self._hidden = {}

    def update(self) -> Mapping[str, float]:
        config = self._config
        trajectories = [t for t in self._buffer if t.steps]
        self._buffer = []
        if not trajectories:
            return {"trajectories": 0.0}

        # GAE per trajectory from the collection-time values (terminal V = 0:
        # every trajectory ends with the episode, truncated ones carry the
        # documented terminal penalty in their reward tail).
        advantages: list[torch.Tensor] = []
        returns: list[torch.Tensor] = []
        for trajectory in trajectories:
            values = [step.value for step in trajectory.steps] + [0.0]
            adv = [0.0] * len(trajectory.steps)
            running = 0.0
            for t in reversed(range(len(trajectory.steps))):
                delta = trajectory.rewards[t] + config.gamma * values[t + 1] - values[t]
                running = delta + config.gamma * config.gae_lambda * running
                adv[t] = running
            advantages.append(torch.tensor(adv, dtype=_DTYPE))
            returns.append(
                torch.tensor(
                    [a + v for a, v in zip(adv, values[:-1], strict=True)],
                    dtype=_DTYPE,
                )
            )
        flat_adv = torch.cat(advantages)
        adv_mean = flat_adv.mean()
        adv_std = flat_adv.std(unbiased=False).clamp_min(1e-8)
        advantages = [(a - adv_mean) / adv_std for a in advantages]

        stats = {
            "trajectories": float(len(trajectories)),
            "decisions": float(sum(len(t.steps) for t in trajectories)),
            "mean_return": float(torch.cat(returns).mean().item() if returns else 0.0),
        }
        for _ in range(config.epochs_per_update):
            self._optimizer.zero_grad()
            policy_losses: list[torch.Tensor] = []
            value_losses: list[torch.Tensor] = []
            entropies: list[torch.Tensor] = []
            anchor_terms: list[torch.Tensor] = []
            for trajectory, adv, ret in zip(
                trajectories, advantages, returns, strict=True
            ):
                features = torch.tensor(
                    [list(step.features) for step in trajectory.steps],
                    dtype=_DTYPE,
                )
                logits, values, _ = self._net.forward_sequence(features)
                old_log_probs = torch.tensor(
                    [step.log_prob for step in trajectory.steps], dtype=_DTYPE
                )
                new_log_probs: list[torch.Tensor] = []
                for index, step in enumerate(trajectory.steps):
                    scores = _candidate_scores(logits[index], step.recipes)
                    log_softmax = torch.log_softmax(scores, dim=0)
                    new_log_probs.append(log_softmax[step.action])
                    probs = torch.exp(log_softmax)
                    entropies.append(-(probs * log_softmax).sum())
                    if step.fsm_index is not None:
                        anchor_terms.append(-log_softmax[step.fsm_index])
                new_lp = torch.stack(new_log_probs)
                ratio = torch.exp(new_lp - old_log_probs)
                clipped = torch.clamp(
                    ratio, 1.0 - config.clip_ratio, 1.0 + config.clip_ratio
                )
                policy_losses.append(-torch.min(ratio * adv, clipped * adv).sum())
                value_losses.append(((values - ret) ** 2).sum())
            decisions = stats["decisions"]
            policy_loss = torch.stack(policy_losses).sum() / decisions
            value_loss = torch.stack(value_losses).sum() / decisions
            entropy = torch.stack(entropies).sum() / decisions
            anchor_ce = (
                torch.stack(anchor_terms).sum() / len(anchor_terms)
                if anchor_terms
                else torch.zeros((), dtype=_DTYPE)
            )
            loss = (
                policy_loss
                + config.value_coef * value_loss
                + config.anchor_coef * anchor_ce
                - config.entropy_coef * entropy
            )
            loss.backward()
            nn.utils.clip_grad_norm_(self._net.parameters(), config.max_grad_norm)
            self._optimizer.step()
        self._updates_done += 1
        stats.update(
            {
                "policy_loss": float(policy_loss.item()),
                "value_loss": float(value_loss.item()),
                "entropy": float(entropy.item()),
                "anchor_ce": float(anchor_ce.item()),
                "updates_done": float(self._updates_done),
            }
        )
        return stats

    def frozen_scorer(self) -> FrozenGruScorer:
        frozen = GruPolicyValueNet(
            input_dim=self._config.input_dim,
            hidden=self._config.hidden,
            head=self._config.head,
        ).to(_DTYPE)
        frozen.load_state_dict(self._net.state_dict())
        return FrozenGruScorer(frozen)

    def flat_weights(self) -> tuple[float, ...]:
        return flat_parameters(self._net)

    def config(self) -> Mapping[str, object]:
        return {
            **self._config.as_config(),
            "architecture": "linear-tanh -> GRU -> policy/value heads",
            "parameter_count": sum(p.numel() for p in self._net.parameters()),
            "dtype": "float64",
            "torch_version": torch.__version__,
            "torch_num_threads": torch.get_num_threads(),
        }


def scorer_from_artifact(
    config: Mapping[str, object], weights: Sequence[float]
) -> FrozenGruScorer:
    """Rebuild the frozen scorer from a 15.15 artifact (config + flat genome)."""

    net = build_net_from_config(config)
    load_flat_parameters(net, weights)
    return FrozenGruScorer(net)
