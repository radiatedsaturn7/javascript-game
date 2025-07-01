# 🏁 ASCII Racer: Terminal Velocity

Welcome to **ASCII Racer**, the most violently nostalgic 2.5D racing game you never asked for.

Blistering speed. Exploding pixels. A track made entirely of slashes and pipes.  
This ain't just a game—it's a **high-octane hallucination in your terminal**.

---

## 🚀 Features

- Fast-paced pseudo-3D perspective racing in pure ASCII
- Curving tracks, lane switching, and procedural chaos
- Dodge obstacles, hug curves, and pray to the frame gods
- Written in Python using `curses` like a true masochist

---

## 📦 Requirements

### 🔧 Runtime:
- Python **3.8+**
- Works best in **Unix/Linux terminals**
  - Windows users: install [`windows-curses`](https://pypi.org/project/windows-curses/) via pip

### 📚 Python Packages:
```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
```txt
windows-curses ; sys_platform == 'win32'
```
_(Yeah, that's it—`curses` is built-in on Unix. Windows just needs a little help.)_

---

## 🕹 Controls

| Key | Action                     |
|-----|----------------------------|
| ←   | Steer Left                 |
| →   | Steer Right                |
| ↑   | Pitch Up (air only)        |
| ↓   | Pitch Down (air only)      |
| Space | Throttle / Accelerate   |
| B   | Boost (costs health)       |
| Q   | Quit                       |

---

## 🛠 Project Structure

```
ascii-racer/
├── game.py             # Main game loop and render engine
├── track.py            # Track segment logic and generation
├── player.py           # Your scrappy little ASCII racer
├── README.md           # This glorious document
├── requirements.txt    # Python packages (only for Windows)
```

---

## 💡 Concept

We're faking 3D in a 2D world using **scaled perspective**, **line skewing**, and **raw terminal power**.  
The track flies toward you. You move left and right. Everything else is illusion.

---

## 🧪 Known Issues

- It runs in a terminal. Don't expect ray tracing.
- Frame rates may vary depending on your soul and system load.
- You may develop uncontrollable urges to wear a leather jacket and flip off polygons.

---

## ❤️ Credits

Created by someone with too much imagination and not enough GPU.  
Powered by the ghost of old arcade machines and the spirit of "what if?"

---

## 🧠 Coming Soon (Maybe?)

- AI opponents (`E`)
- Boost pads (`+`)
- Crashes & explosions (`#`)
- Custom tracks?
- Online leaderboards (for terminal gremlins only)

---

## 🧵 License

MIT, because chaos should be free.

---

**Run fast. Turn hard. Dodge ASCII death.**
