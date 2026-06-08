# Opening accusations — baseline vs decisive, both models


## 1:headless-seed-1:meeting-0:p-8  (impostors: ['p-6', 'p-7'])

**qwen2.5:7b-instruct / baseline** — accused `p-6` (impostor=True, conf=0.7):
> I found p-4's body in ADMIN at tick 8. I saw p-6 and p-7 there as well, which is unusual given the time of day. I'm not sure yet who to blame, but these sightings are concerning.

**qwen2.5:7b-instruct / report_decisive** — accused `p-6` (impostor=True, conf=0.7):
> I found p-4's body in ADMIN at tick 8. I saw both p-6 and p-7 in ADMIN around the same time, which is suspicious given that only one of them could have killed p-4. Given their proximity to the scene, I believe p-6 or p-7 is most likely the culprit.

**qwen3.5:9b / baseline** — accused `p-6` (impostor=True, conf=0.5):
> I discovered p-4's body in ADMIN at tick 8. At that exact moment, I saw both p-6 and p-7 present in the room with me. Since they were co-present when the kill occurred, neither could have performed it alone without a vent or another crewmate helping them; however, given their proximity to the scene immediately after discovery, my suspicion is highest on one of them.

**qwen3.5:9b / report_decisive** — accused `p-6` (impostor=True, conf=0.85):
> I found p-4's body in ADMIN at tick 8. I was there with p-6 and p-7 when the kill happened; however, my logs show both of them were already present in ADMIN as early as tick 7 while others like p-2 were still moving around Engineering or East Hall. This places significant pressure on who had access to Admin before me. Based on their suspicious presence near the body at a critical time and conflicting movement patterns compared to other crewmates, I am accusing p-6 with high confidence.