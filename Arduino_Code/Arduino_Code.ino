int analogPin = 9;

void setup(){
  Serial.begin(9600);
  pinMode(analogPin, OUTPUT);
}

void loop(){
  if (Serial.available()) {
    delay(100);
    while (Serial.available() > 0) {
      int x = Serial.read();
      x = map(x, 0, 100, 0, 255);
      analogWrite(analogPin, x);
    }
  }
}
