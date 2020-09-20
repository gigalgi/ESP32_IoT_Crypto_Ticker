// importa la libreria para manejo de lcd
#include <LiquidCrystal.h>

// se iniciliza la libreria y se asignan los pines de conexion
// with the arduino pin number it is connected to
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

String ltc; 
String btc;

void setup() {
  // se fijan el numero de filas y columnas del lcd
  lcd.begin(16, 2);
  // inicia la comunicacion serial
  // se limpia la pantalla
  lcd.clear();
  Serial.begin(9600);
}

void loop() {
  // se verifica si se a recibido datos por el puerto serie
  if (Serial.available()) {
    // esperamos a recibir el mensaje 
    delay(100);
    // se leen los vslores que llegan por el puerto serie
    while (Serial.available() > 0) {
      //se lee el string hasta el carater finalizador fijado en este caso '$'      
      ltc=Serial.readStringUntil('$');
      //se ubica el cursor para escribir en la primera fila de la pantalla
      lcd.setCursor(0, 0);
      // se escribe en la pantalla
      lcd.print(ltc);
      //se lee el string hasta el segundo carater finalizador fijado en este caso ':'  
      btc=Serial.readStringUntil(':');
      //se pone el cursor en la segunda filla
      lcd.setCursor(0, 1);
      // se escribe en la pantalla
      lcd.print(btc);
      
    }
  }
}
