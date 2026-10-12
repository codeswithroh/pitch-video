# Nightfall: pitch / demo video script

**Target length:** ~2:20 · **~340 words** · read calmly, with energy on the bold lines.

## How to record (so I can sync it perfectly)

- **Landscape, 1080p**, face and shoulders, plain background, quiet room. Look at the camera.
- **Clap once** on camera before you start (my sync marker).
- Read **one scene at a time**, then **pause ~2 seconds** before the next. Re-read a scene if you stumble; I'll use the last take.
- Don't worry about matching the gameplay: I'll cut the gameplay to your voice.

---

### Scene 1 · Hook (0:00–0:12)
*On screen: black → NIGHTFALL title card → your hero by the campfire, shadows lurking.*

> Every onchain game is played with the cards face up.
> If it lives on the blockchain, anyone can read it — including **where your opponent is hiding**.

### Scene 2 · The problem (0:12–0:27)
*On screen: quick montage: RPC call returning raw data → the fog-of-war arena from above.*

> That's why fog of war — the heart of strategy games and battle royales — has basically been impossible onchain.
> Until now.

### Scene 3 · Introduce Nightfall (0:27–0:45)
*On screen: title screen, cycling skins / hats / capes, switching arenas and day/night.*

> This is **Nightfall**: a real-time battle royale on Solana where you only see what your torch lights.
> Pick your hero, pick your arena, night or day — and hit play.
> No wallet popups, no setup.

### Scene 4 · Onboarding (0:45–0:58)
*On screen: warm-up yard: walking, hitting the dummy, shooting, blinking; setup steps ticking off; "THE NIGHT IS READY".*

> While the arena spins up onchain, you warm up: walk, hit the dummy, shoot, blink.
> By the time the night is ready, you already know how to play.

### Scene 5 · The gameplay (0:58–1:22)
*On screen: drop in → dark arena, torchlight → red hearing arcs → enemy steps into the light → fight, damage numbers, kill streak → chest loot (axe, pearl) → border closing.*

> Out here, **you can't see anyone**. You can only hear them — footsteps from the dark, coming from the south-west.
> Then someone steps into your light.
> Grab a battle axe, a war hammer, an ender pearl — and stay inside the border. **Last one standing wins.**

### Scene 6 · The proof: try to cheat (1:22–1:42)
*On screen: press X → X-ray panel: World null, opponents' Visions null, your Vision readable.*

> And here's the part that matters. Let's try to cheat.
> I'll ask the network for every player's position… **null**. The other players' views… **null**.
> Even I — the host who created this match — **can't see them**.

### Scene 7 · How it works (1:42–2:02)
*On screen: architecture diagram animating in; labels: Ephemeral Rollup · Private ER (TEE) · VRF · Crank.*

> Every position is sealed inside **MagicBlock's Private Ephemeral Rollup** — an Intel TDX enclave.
> Each move runs inside it and writes each player only what *they* are allowed to see.
> **VRF** rolls the spawns, a **crank** shrinks the border, and every step is a real-time, gasless transaction.

### Scene 8 · Spectate & verify (2:02–2:14)
*On screen: spectator view following players with the delay badge → match ends → "Reveal the night" → settle → winner paid on Solana.*

> Spectators watch everyone on a short broadcast delay, so nobody can feed them positions.
> And when the night ends, the world is revealed and the winner is paid onchain.

### Scene 9 · Close (2:14–2:22)
*On screen: hero by the campfire → logo, play link, GitHub link.*

> **Nightfall. Everyone's in the dark — even the server.**
> Come play.
