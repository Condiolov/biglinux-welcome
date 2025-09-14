#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-welcome

# Assign the received arguments to variables with clear names
browser="$1"
originalUser="$2"
userDisplay="$3"
userXauthority="$4"
userDbusAddress="$5"
userLang="$6"
userLanguage="$7"

# Helper browser to run a command as the original user
runAsUser() {
  # Single quotes around variables are a good security practice
  su "$originalUser" -c "export DISPLAY='$userDisplay'; export XAUTHORITY='$userXauthority'; export DBUS_SESSION_BUS_ADDRESS='$userDbusAddress'; export LANG='$userLang'; export LC_ALL='$userLang'; export LANGUAGE='$userLanguage'; $1"
}

# 1. Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/browser_install_pipe_$$"
mkfifo "$pipePath"

# 2. Starts Zenity IN THE BACKGROUND, as the user, with the full environment
zenityTitle=$"Browser Install"
zenityText=$'Instaling Browser, Please wait...'
runAsUser "zenity --progress --title='Install Browser' --text=\"$zenityText\" --pulsate --auto-close --no-cancel < '$pipePath'" &

# 3. Executes the root tasks.
installBrowser() {
  if [[ "$browser" == "brave" ]]; then
    pacman -Syu --noconfirm brave
  elif [[ "$browser" == "firefox" ]]; then
    pacman -Syu --noconfirm firefox
  elif [[ "$browser" == "google-chrome" ]]; then
    pamac-installer --build google-chrome
  elif [[ "$browser" == "librewolf" ]]; then
    pamac-installer --build librewolf-bin
  fi
  exitCode=$?
}
installBrowser > "$pipePath"
# sleep 2 > "$pipePath"

# 4. Cleans up the pipe
rm "$pipePath"

# 5. Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" -eq 0 ]]; then
  zenityText=$"Browser installed successfully!"
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"An error occurred while install browser."
  runAsUser "zenity --error --text=\"$zenityText\""
fi

# 6. Exits the script with the correct exit code
exit $exitCode
