/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow
 */

import React, { Component } from "react"
import { BleManager } from "react-native-ble-plx"
import {
  AppRegistry,
  StyleSheet,
  Text,
  View,
  Button,
  TouchableHighlight,
  NativeAppEventEmitter,
  NativeEventEmitter,
  NativeModules,
  Platform,
  PermissionsAndroid,
  ListView,
  ScrollView,
  AppState,
  Dimensions
} from "react-native"

import { decode as atob, encode as btoa } from "base-64"

import { format } from "date-fns"

const instructions = Platform.select({
  ios: "Press Cmd+R to reload,\n" + "Cmd+D or shake for dev menu",
  android:
    "Double tap R on your keyboard to reload,\n" +
    "Shake or press menu button for dev menu"
})

export default class App extends Component {
  constructor() {
    super()
    this.state = { status: "START", device: null, values: {} }
    this.manager = new BleManager()
  }

  componentDidMount() {
    this.scanAndConnect()
    this.checkPermissions()
  }

  checkPermissions = () => {
    if (Platform.OS === "android" && Platform.Version >= 23) {
      PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION
      ).then(result => {
        if (result) {
          console.log("Permission is OK")
        } else {
          PermissionsAndroid.requestPermission(
            PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION
          ).then(result => {
            if (result) {
              console.log("User accept")
            } else {
              console.log("User refuse")
            }
          })
        }
      })
    }
  }

  disconnect = () => {
    const { device } = this.state
    if (device) {
      device
        .cancelConnection(device.id)
        .then(ok => console.log("disconnected", ok))
        .catch(err => console.log("error during disconnession"))
    }
  }

  scanAndConnect = () => {
    this.setState({ status: "SCANNING" })

    this.manager.startDeviceScan(null, null, (error, device) => {
      if (error) {
        // Handle error (scanning will be stopped automatically)
        console.log("ERROR", error)
        return
      }

      console.log("device", device, device.name)

      // Check if it is a device you are looking for based on advertisement data
      // or other criteria.
      if (device.name && device.name.startsWith("puez")) {
        // Stop scanning as it's not necessary if you are scanning for one device.
        this.manager.stopDeviceScan()
        console.log("TROVATO")
        // Proceed with connection.

        this.manager
          .connectToDevice(device.id)
          .then(aa => {
            this.setState({ device })
            console.log("connesso", aa)
            this.setState({ status: "connected" })

            device
              .discoverAllServicesAndCharacteristics()
              .then(device => {
                console.log(device.serviceData)
                device
                  .services()
                  .then(services => {
                    this.setState({ services })
                    this.readThings()
                    console.log("services", services)
                  })
                  .catch(err => console.error(err))
              })
              .catch(err => console.log("error in discovery", err))
          })
          .catch(err => console.log("errore", err))
      }
    })
  }

  readThings = async () => {
    const { services } = this.state

    const promises = services.map(service => {
      service
        .characteristics()
        .then(chars => {
          console.log(">>> ", chars)
          chars.forEach(char => {
            console.log(">>>>>> ", char)

            char
              .read()
              .then(c => {
                char.monitor((err, newChar) => {
                  if (err) console.log("ERRORE IN MONITOR", err)
                  else {
                    console.log("> <.<.<.<>><.,'", newChar)
                    this.onChange(service.uuid, char.uuid, atob(newChar.value))
                  }
                })
                this.onChange(service.uuid, char.uuid, atob(c.value))
                // console.log(this.state.values)
                console.log(">>> >> >> >>>", c, atob(c.value))
                if (c.uuid == "00000007-0000-1000-8000-00805f9b34fb") {
                  console.log(
                    "provo a scrivere",
                    "npretto " + format(new Date(), "YYYY-MM-DD-HH-mm-ss")
                  )
                  c.writeWithoutResponse(
                    btoa("npretto " + format(new Date(), "YYYYMMDDHHmmss"))
                  )
                }
              })
              .catch(err => console.warn(err))
          })
        })

        .catch(err => console.error(err))
    })

    // Promises.all(services.characteristics())
    // .then(characteristics => )

    console.log(stuff)

    // const stuff = await services.map(async s => await s.characteristics());
    // Promise.all(stuff).then(async c => console.log(await c.read()));
  }

  onChange = async (serviceUUID, charUUID, value) => {
    const values = this.state.values
    const service = this.state.values[serviceUUID] || {}

    await this.setState({
      values: { ...values, [serviceUUID]: { ...service, [charUUID]: value } }
    })
  }

  get = key => {
    try {
      return this.state.values["00000000-0000-1000-8000-00805f9b34fb"][key]
    } catch (err) {
      return " ¯\\_(ツ)_/¯"
    }
  }

  DataBox = props => (
    <View style={styles.DataBox}>
      <Text> {props.name}</Text>
      <Text> {props.value}</Text>
    </View>
  )

  render() {
    const { device, status, values } = this.state

    const temperature = this.get("00000001-0000-1000-8000-00805f9b34fb")
    const light = this.get("00000002-0000-1000-8000-00805f9b34fb")
    const flame = this.get("00000003-0000-1000-8000-00805f9b34fb")
    const humidity = this.get("00000004-0000-1000-8000-00805f9b34fb")
    const windSpeed = this.get("00000005-0000-1000-8000-00805f9b34fb")
    const windDirection = this.get("00000006-0000-1000-8000-00805f9b34fb")

    return (
      <View style={styles.container}>
        <Text> {`Status: ${status} `}</Text>

        {device && (
          <View>
            <Button
              onPress={this.disconnect}
              title={"Station : " + device.name}
              color="#841584"
              accessibilityLabel="Disconnect from the ble thing"
            />
          </View>
        )}
        <View style={styles.DataBoxContainer}>
          <this.DataBox name="Temperature" value={`${temperature}°C`} />
          <this.DataBox name="Light" value={`${light} lx`} />

          <this.DataBox name="Flame" value={flame} />

          <this.DataBox name="Humidity" value={`${humidity}%`} />
          <this.DataBox name="WindSpeed" value={`${windSpeed} m/s`} />
          <this.DataBox name="Wind direction" value={`${windDirection}°`} />
        </View>

        {/* <Text>{JSON.stringify(values)}</Text> */}
      </View>
    )
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#5497A7"
  },
  DataBoxContainer: {
    backgroundColor: "#5497A7",
    flex: 1,
    flexDirection: "row",
    flexWrap: "wrap",
    alignItems: "center",
    justifyContent: "space-around"
  },
  DataBox: {
    justifyContent: "center",
    alignItems: "center",
    padding: 10,
    borderRadius: 10,
    marginBottom: 40,
    width: "40%",
    height: 120,
    backgroundColor: "#78CAD2"
  },
  instructions: {
    textAlign: "center",
    color: "#333333",
    marginBottom: 5
  }
})
