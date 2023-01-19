int light;
int rep, sleep, scale, i;
////
int red_pin = 11;
int green_pin = 10;
int blue_pin = 9;
////
int intensity, intensity_o, intensity_y;
char status[2]; 
const char* ok = "ok";

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);

  // Definicion de los pines del LED RGB
  pinMode(red_pin, OUTPUT);
  pinMode(green_pin, OUTPUT);
  pinMode(blue_pin, OUTPUT);
  RGB_color(255, 255, 255);

  // Enviar un 1 para avisar que esta listo para recibir los parametros
  Serial.print(1);

  /* Recepcion de parametros:
    Se espera hasta que Python confirme que los parametros 
    en el arduino coinciden con los enviados.*/
  while (strcmp(status,ok)){
    while (!Serial.available());
    String params = Serial.readString();
    sscanf(params.c_str(), "%s%d %d %d %d", &status, &rep, &sleep, &scale, &i);
    if (!strcmp(status,ok)) break;
    Serial.println(rep);Serial.println(sleep);Serial.println(scale);Serial.println(i);
    delay(10);
  }

  // Se define en cuanto varian las componentes del LED RGB para lograr la intensidad deseada 
  intensity = 255*i / scale; intensity_o = 45*i / scale; intensity_y = 90*i / scale;

  /* Toma y envio de datos segun la cantidad de repeticiones (rep),
     el delay entre cada toma de datos (delay) 
     y las intensidades de los colores definidas previamente (con scale e i) */
  for (int j = 0; j < rep; j++) {
    RGB_color(255 - intensity, 255, 255);  // Red
    delay(sleep);
    light = analogRead(A0);
    Serial.print(light);
    // Se envian comas para separar los datos y posteriormente crear un archivo csv
    Serial.print(","); 

    // Se apaga el LED y se espera un segundo para que el fotorresistor recalibre
    RGB_color(255, 255, 255); 
    delay(1000);

    RGB_color(255 - intensity, 255 - intensity_o, 255);  // Orange
    delay(sleep);
    light = analogRead(A0);
    Serial.print(light);
    Serial.print(","); 

    RGB_color(255, 255, 255);
    delay(1000);

    RGB_color(255 - intensity, 255 - intensity_y, 255);  // Yellow
    delay(sleep);
    light = analogRead(A0);
    Serial.print(light);
    Serial.print(",");

    RGB_color(255, 255, 255);
    delay(1000);

    RGB_color(255, 255 - intensity, 255);  // Green
    delay(sleep);
    light = analogRead(A0);
    Serial.print(light);
    Serial.print(",");

    RGB_color(255, 255, 255);
    delay(1000);

    RGB_color(255, 255 - intensity, 255 - intensity);  // Cyan
    delay(sleep);
    light = analogRead(A0);
    Serial.print(light);
    Serial.print(",");

    RGB_color(255, 255, 255);
    delay(1000);

    RGB_color(255, 255, 255 - intensity);  // Blue
    delay(sleep);
    light = analogRead(A0);
    Serial.print(light);
    Serial.print(",");

    RGB_color(255, 255, 255);
    delay(1000);

    RGB_color(255 - intensity, 255, 255 - intensity);  // Magenta
    delay(sleep);
    light = analogRead(A0);
    Serial.print(light);
    Serial.println();

    RGB_color(255, 255, 255);
    delay(1000);
  }
}

void loop() {
}

void RGB_color(int red_value, int green_value, int blue_value) {
  analogWrite(red_pin, red_value);
  analogWrite(green_pin, green_value);
  analogWrite(blue_pin, blue_value);
}