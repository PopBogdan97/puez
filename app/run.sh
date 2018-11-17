adb kill-server
lsof -P | grep ':8081' | awk '{print $2}' | xargs kill -9
adb reverse tcp:8081 tcp:8081
adb devices
react-native start