## Backend Setup 
1. Install Docker Desktop:  https://docs.docker.com/get-docker/
2. Once installed, make sure to open `Docker Desktop` and make sure bottom left says `engine running` and it's green.
3. Make sure you are in the project directory
4. Run command in terminal: `docker build -t backend-container .`
5. Run command to run backend locally: `docker run -p 5000:5000 backend-container`
6. Verify your backedn is up and running by going to your browser and type in the address bar `http://127.0.0.1:5000/test`, then you should see this `{"Backend":"Up and Running!!"}`

## Frontend Setup
1. Install NVM by running this command: `bash install_nvm.sh`
3. Then run this command: `source ~/.bash_profile`
4. Verify you have it installed by running this command: `command -v nvm` and you should have gotten this back `nvm`
5. In the project directory run this command to install Node: `nvm install`, and Node.js should have been installed.
6. Go into `frontend` directory: `cd directory`
7. Run `npm install` to install all of the packages.
8. Run command to run frontend locally: `npm start:offline`
7. Verify your frontend is up and running by going to your browser and type in the address bar `http://127.0.0.1:3000`, then you should see the app running.