int light;
int rep, sleep, cant;
////
int red_pin = 11;
int green_pin = 10;
int blue_pin = 9;
////
int i;
int step, step_o, step_y;

void setup() {
  Serial.begin(115200); 
  Serial.setTimeout(1);
  
  pinMode(red_pin, OUTPUT);
  pinMode(green_pin, OUTPUT);
  pinMode(blue_pin, OUTPUT);
  RGB(255, 255, 255);
  
  // Recepcion de los datos enviados por Python
  Serial.print(1);
  while (!Serial.available());
  String params = Serial.readString();
  sscanf(params.c_str(), "%d %d %d", &rep, &sleep, &cant);
  
  // Definicion de los pasos a los que se varian los valores del LED RGB
  step = 255 / cant; step_o = 45 / cant; step_y = 90 / cant;

  /* Toma de datos segun el numero de repeticiones (rep),
     el delay entre cada medicion (sleep) y
     la cantidad de intensidades por cada color (cant)*/ 
  for (int j = 0; j < rep; j++) {
    for (i = 1; i <= cant; i++) {
      light = analogRead(A0);
      Serial.print(light);
      // Se envian comas para separar los datos y posteriormente crear un archivo csv
      Serial.print(",");

      RGB(255 - step * i, 255, 255);  // Red
      delay(sleep);
    }
    Serial.println();

    // Se apaga el LED y se espera un segundo para que el fotorresistor recalibre
    RGB(255, 255, 255);
    delay(1000);

    for (i = 1; i <= cant; i++) {
      light = analogRead(A0);
      Serial.print(light);
      Serial.print(",");

      RGB(255 - step * i, 255 - i * step_o, 255);  // Orange
      delay(sleep);
    }
    Serial.println();

    RGB(255, 255, 255);
    delay(1000);

    for (i = 1; i <= cant; i++) {
      light = analogRead(A0);
      Serial.print(light);
      Serial.print(",");

      RGB(255 - step * i, 255 - i * step_y, 255);  // Yellow
      delay(sleep);
    }
    Serial.println();

    RGB(255, 255, 255);
    delay(1000);

    for (i = 1; i <= cant; i++) {
      light = analogRead(A0);
      Serial.print(light);
      Serial.print(",");

      RGB(255, 255 - step * i, 255);  // Green
      delay(sleep);
    }
    Serial.println();

    RGB(255, 255, 255);
    delay(1000);

    for (i = 1; i <= cant; i++) {
      light = analogRead(A0);
      Serial.print(light);
      Serial.print(",");

      RGB(255, 255 - step * i, 255 - step * i);  // Cyan
      delay(sleep);
    }
    Serial.println();

    RGB(255, 255, 255);
    delay(1000);

    for (i = 1; i <= cant; i++) {
      light = analogRead(A0);
      Serial.print(light);
      Serial.print(",");

      RGB(255, 255, 255 - step * i);  // Blue
      delay(sleep);
    }
    Serial.println();

    RGB(255, 255, 255);
    delay(1000);

    for (i = 1; i <= cant; i++) {
      light = analogRead(A0);
      Serial.print(light);
      Serial.print(",");

      RGB(255 - step * i, 255, 255 - step * i);  // Magenta
      delay(sleep);
    }
    Serial.println();

    RGB(255, 255, 255);
    delay(1000);
  }

}

void loop() {
  }

// Defición de la escritura en el LED RGB
void RGB(int red_value, int green_value, int blue_value) {
  analogWrite(red_pin, red_value);
  analogWrite(green_pin, green_value);
  analogWrite(blue_pin, blue_value);
}