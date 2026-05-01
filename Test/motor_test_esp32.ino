#define stepPin 16
#define dirPin 17
#define enablePin 18
#define limitPin 34   // VEX limit switch NC pin → ESP32 GPIO 34

const int stepsPerRevolution = 3200; // microstep setting

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(limitPin, INPUT_PULLUP);  // NC wiring → HIGH normally, LOW when pressed

  digitalWrite(enablePin, LOW); // enable TB6600
  Serial.begin(9600);
}

// Move motor by a specific number of degrees
void moveDegrees(float degrees, bool direction) {
  digitalWrite(dirPin, direction ? HIGH : LOW);

  int stepsToMove = (int)(degrees * (stepsPerRevolution / 360.0));

  for (int i = 0; i < stepsToMove; i++) {

    // stop check
    if (digitalRead(limitPin) == HIGH) {
      Serial.println("LIMIT SWITCH TRIGGERED — MOTOR STOPPED");
      return;  // exit immediately
    }

    digitalWrite(stepPin, HIGH);
    delayMicroseconds(200);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(200);
  }
}

void loop() {
  // Print switch state for testing
  if (digitalRead(limitPin) == LOW) {
    Serial.println("Switch pressed");
  } else {
    Serial.println("Switch not pressed");
  }

  delay(300);  // slow down serial output

  // Try moving the motor — it will stop if the switch is hit
  moveDegrees(900, true);
  delay(1000);

  moveDegrees(900, false);
  delay(1000);
}