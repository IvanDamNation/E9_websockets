# Websockets test

Made for practice exercise in chapter "Fullstack_F9 module" for SkillFactory

Creates room based on websocket. Everyone who have the "Connected" status receives news. News can be obtained by app via POST request method.

Contains server and client part.


How to use:
1. Clone this repo with `git clone` command.
2. Make new virtual environment `python -m venv venv`.
3. Activate it `\venv\Scripts\activate`.
4. Install requirements from "requirements.txt" `pip install -r requirements.txt`.
5. Run server `py aiohttp_server.py`.
6. Open client page(s) in browser on address `127.0.0.1:8080 (localhost:8080)`.
7. Push "connect" button.
8. You can send news via POST requests on `127.0.0.1:8080/news`


For education purpose only. Workability is not guarantee.

Made by IvanDamNation (a.k.a. IDN) GNU General Public License v3, 2023