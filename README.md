# First-Person Raiden (Working Title)

This project aims to translate the fast-paced arcade action of classic shooters like **RAIDEN II** into a first-person perspective. It is intentionally lightweight so that it can run inside a regular web browser without the need for heavy engines or powerful hardware.

## Overview

- **Genre:** First-person shooter with scripted enemy patterns inspired by classic top-down shooters.
- **Engine:** JavaScript-based. The goal is to load and test the game directly by opening `index.html` in a browser. Engines such as **Three.js** or **Babylon.js** are candidates since they can render 3D scenes through WebGL while remaining lightweight.
- **Graphics:** Low barrier—simple shapes (cubes, cones, cylinders, triangles) with minimal animations. Focus on gameplay and imaginative weapons rather than visual fidelity.

## Core Gameplay

1. **The Super Weapon**
   - The player equips one primary gun that can morph into different firing modes.
   - Think of it as a blend of a chronocepter, quad rocket launcher, and energy cannon all in one package.
   - Switching modes is instantaneous, and the weapon can fire multiple types of shots simultaneously.

2. **Enemy Patterns**
   - Hostile robots attack in waves, following predetermined formations similar to the enemy patterns in *Gradius* or *RAIDEN II*.
   - Some enemies dive from above, others strafe across the player’s view, and bosses have several distinct phases.

3. **Fast-Paced Action**
   - Movement is quick, and enemies swarm the player relentlessly. The intent is to keep the adrenaline high, just like the arcade classics.
   - Levels are short but challenging—perfect for quick sessions or high-score attempts.

4. **Power-Ups and Wingmen**
   - Destroyed enemies drop pick-ups that upgrade the super weapon.
   - Each upgrade visibly changes the gun—new barrels, glowing parts, or extra attachments.
   - Certain pick-ups spawn wingman drones that mirror your shots, multiplying firepower.
   - Upgrades can also unlock side weapons, such as homing missiles that launch alongside normal fire.

## Weapons and Power-Ups

- **Energy Blaster** – Rapid-fire beams that shred lesser robots.
- **Quad Rocket Launcher** – Launches a spread of rockets for area damage.
- **Nuke Cannon** – A slow-firing but devastating explosive shot.
- **Time Distorter** – Temporarily slows down enemies, giving the player breathing room.
- **Homing Missiles** – Secondary rockets that track foes whenever the player fires.

These modes are all packed into the same super weapon, so players can swap between them without changing guns.

## Development Workflow

1. Clone the repository on any machine (even a Chromebook).
2. Install dependencies, if any, using `npm install`.
3. Open `index.html` in a modern browser to run the game. No need for a heavy IDE or runtime.

During early prototypes, development can remain entirely in JavaScript/HTML/CSS. If the project grows, we can introduce additional build tooling, but the core requirement is that the game remains easy to test locally.

## Future Ideas

- Online leaderboards to track high scores.
- Co-op mode where multiple players join in via WebSockets.
- Unlockable weapon upgrades to encourage replay value.

## Contributing

This repository now includes a small playable demo built with [Three.js](https://threejs.org/).
Open `index.html` in any modern browser to test it. The demo features:

* Two primary weapons: a rapid yet inaccurate machine gun and a slower, accurate laser.
* Homing missiles as a side weapon (press **F**).
* Orange "wingman" spheres that follow the player and mirror shots.
* Two enemy types: red chargers that rush the player and blue shooters that wander and fire back.

Feel free to fork the project or open issues to discuss ideas. The goal is still to create a fun, frantic arcade experience with an emphasis on creative weaponry and accessibility.

