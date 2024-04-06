/*
DIY Electronic Shelf Label Management System
Distributed under the MIT License
© Copyright Maxim Bortnikov 2024
For more information please visit
https://sourceforge.net/projects/esl-management-system/
https://github.com/Northstrix/Electronic-Shelf-Label-Management-System
Required libraries:
https://github.com/me-no-dev/ESPAsyncUDP
https://github.com/adafruit/Adafruit-GFX-Library
https://github.com/adafruit/Adafruit_BusIO
https://github.com/adafruit/Adafruit_ILI9341
https://github.com/adafruit/Adafruit-ST7735-Library
https://github.com/Northstrix/AES_in_CBC_mode_for_microcontrollers
*/
#include "ESP8266TrueRandom.h"
#include <EEPROM.h>
#include "aes.h"
#include <ESP8266WiFi.h>
#include "ESPAsyncUDP.h"
#include "FS.h"
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

#define TFT_CS D2   // TFT CS  pin is connected to NodeMCU pin D2
#define TFT_RST D3  // TFT RST pin is connected to NodeMCU pin D3
#define TFT_DC D4   // TFT DC  pin is connected to NodeMCU pin D4
                    // SCK (CLK) ---> NodeMCU pin D5 (GPIO14)
                    // MOSI(DIN) ---> NodeMCU pin D7 (GPIO13)

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

#define DISPLAY_WIDTH 320
#define DISPLAY_HEIGHT 240

#define EEPROM_SIZE 4095
#define BUTTON_PIN 5

const char * ssid = "Access-Point-Name";
const char * pass = "access_point_password";

int m;
int x;
int y;
uint16_t udp_port;
AsyncUDP udp;

String string_for_data;
byte tmp_st[8];
int decract;
uint8_t array_for_CBC_mode[16];
uint8_t back_aes_key[32];
uint32_t aes_mode[3] = {
  128,
  192,
  256
};
uint8_t aes_key[32];

void back_aes_k() {
  for (int i = 0; i < 32; i++) {
    back_aes_key[i] = aes_key[i];
  }
}

void rest_aes_k() {
  for (int i = 0; i < 32; i++) {
    aes_key[i] = back_aes_key[i];
  }
}

void incr_aes_key() {
  if (aes_key[15] == 255) {
    aes_key[15] = 0;
    if (aes_key[14] == 255) {
      aes_key[14] = 0;
      if (aes_key[13] == 255) {
        aes_key[13] = 0;
        if (aes_key[12] == 255) {
          aes_key[12] = 0;
          if (aes_key[11] == 255) {
            aes_key[11] = 0;
            if (aes_key[10] == 255) {
              aes_key[10] = 0;
              if (aes_key[9] == 255) {
                aes_key[9] = 0;
                if (aes_key[8] == 255) {
                  aes_key[8] = 0;
                  if (aes_key[7] == 255) {
                    aes_key[7] = 0;
                    if (aes_key[6] == 255) {
                      aes_key[6] = 0;
                      if (aes_key[5] == 255) {
                        aes_key[5] = 0;
                        if (aes_key[4] == 255) {
                          aes_key[4] = 0;
                          if (aes_key[3] == 255) {
                            aes_key[3] = 0;
                            if (aes_key[2] == 255) {
                              aes_key[2] = 0;
                              if (aes_key[1] == 255) {
                                aes_key[1] = 0;
                                if (aes_key[0] == 255) {
                                  aes_key[0] = 0;
                                } else {
                                  aes_key[0]++;
                                }
                              } else {
                                aes_key[1]++;
                              }
                            } else {
                              aes_key[2]++;
                            }
                          } else {
                            aes_key[3]++;
                          }
                        } else {
                          aes_key[4]++;
                        }
                      } else {
                        aes_key[5]++;
                      }
                    } else {
                      aes_key[6]++;
                    }
                  } else {
                    aes_key[7]++;
                  }
                } else {
                  aes_key[8]++;
                }
              } else {
                aes_key[9]++;
              }
            } else {
              aes_key[10]++;
            }
          } else {
            aes_key[11]++;
          }
        } else {
          aes_key[12]++;
        }
      } else {
        aes_key[13]++;
      }
    } else {
      aes_key[14]++;
    }
  } else {
    aes_key[15]++;
  }
}

int getNum(char ch) {
  int num = 0;
  if (ch >= '0' && ch <= '9') {
    num = ch - 0x30;
  } else {
    switch (ch) {
    case 'A':
    case 'a':
      num = 10;
      break;
    case 'B':
    case 'b':
      num = 11;
      break;
    case 'C':
    case 'c':
      num = 12;
      break;
    case 'D':
    case 'd':
      num = 13;
      break;
    case 'E':
    case 'e':
      num = 14;
      break;
    case 'F':
    case 'f':
      num = 15;
      break;
    default:
      num = 0;
    }
  }
  return num;
}

char getChar(int num) {
  char ch;
  if (num >= 0 && num <= 9) {
    ch = char(num + 48);
  } else {
    switch (num) {
    case 10:
      ch = 'a';
      break;
    case 11:
      ch = 'b';
      break;
    case 12:
      ch = 'c';
      break;
    case 13:
      ch = 'd';
      break;
    case 14:
      ch = 'e';
      break;
    case 15:
      ch = 'f';
      break;
    }
  }
  return ch;
}

void back_key() {
  back_aes_k();
}

void rest_key() {
  rest_aes_k();
}

void clear_variables() {
  string_for_data = "";
  decract = 0;
}

void disp_centered_text(String text, int h) {
  int16_t x1;
  int16_t y1;
  uint16_t width;
  uint16_t height;
  tft.getTextBounds(text, 0, 0, & x1, & y1, & width, & height);
  tft.setCursor((DISPLAY_WIDTH - width) / 2, h);
  tft.print(text);
}

String read_file(fs::FS & fs, String path) {
  File file = fs.open(path, "r");
  if (!file || file.isDirectory()) {
    return "-1";
  }
  String fileContent;
  while (file.available()) {
    fileContent += String((char) file.read());
  }
  file.close();
  return fileContent;
}

void write_to_file_with_overwrite(fs::FS & fs, String path, String content) {
  File file = fs.open(path, "w");
  if (!file) {
    return;
  }
  file.print(content);
  file.close();
}

bool bttn_is_pressed() {
  bool bt_state = false;
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(350);
    if (digitalRead(BUTTON_PIN) == LOW) {
      bt_state = true;
    }
  }
  return bt_state;
}

void display_line_on_display(String img_line) {
  if (img_line != "-1") {
    for (int i = 0; i < (DISPLAY_WIDTH * 4); i += 4) {
      String hex = "";
      for (int j = 0; j < 4; j++) {
        hex += img_line.charAt(i + j);
      }
      uint16_t color = (uint16_t) strtol(hex.c_str(), NULL, 16);
      tft.drawPixel(x, y, color);
      x++;
      if (x == DISPLAY_WIDTH) {
        x = 0;
        y++;
      }
    }
  }
}

void setup() {
  m = 2; // Set AES to 256-bit mode
  tft.begin();
  tft.fillScreen(0x0000);
  tft.setRotation(1);
  tft.setCursor(0, 5);
  if (!SPIFFS.begin()) {
    tft.println("An Error has occurred while mounting SPIFFS");
    return;
  }
  pinMode(BUTTON_PIN, INPUT);
  Serial.begin(115200);
  if (bttn_is_pressed() == true) {
    disp_centered_text("Open The Serial Terminal", 10);
    disp_centered_text("and switch ESL to operating mode", 30);
    while (bttn_is_pressed() == true) {
      delay(100);
    }
    tft.fillScreen(0x0000);
    disp_centered_text("The Encryption Key and UDP Port", 10);
    disp_centered_text("will be printed to the Serial Terminal", 30);
    disp_centered_text("in 2 seconds", 50);
    delay(2000);
    tft.fillScreen(0x0000);
    EEPROM.begin(EEPROM_SIZE);
    randomSeed(ESP8266TrueRandom.random());
    for (int i = 0; i < 34; i++) {
      EEPROM.write((i), ESP8266TrueRandom.random(0, 256));
    }
    if (EEPROM.read(33) == 0 && EEPROM.read(32) == 0)
      EEPROM.write((33), ESP8266TrueRandom.random(128, 256));

    String extr_eeprom_content;
    for (int i = 0; i < 32; i++) {
      if (EEPROM.read(i) < 16)
        extr_eeprom_content += "0";
      extr_eeprom_content += String(EEPROM.read(i), HEX);
    }
    Serial.println("\nEncryption Key:");
    Serial.println(extr_eeprom_content);

    String extr_udp;
    for (int i = 32; i < 34; i++) {
      if (EEPROM.read(i) < 16)
        extr_udp += "0";
      extr_udp += String(EEPROM.read(i), HEX);
    }

    Serial.println("UDP Port:");
    Serial.println(extr_udp);
    Serial.println();
    EEPROM.end();
    disp_centered_text("Check the Serial Terminal", 10);
  } else {
    delay(500);
    if (read_file(SPIFFS, "Line1") != "-1") {
      x = 0;
      y = 0;
      for (int i = 0; i < DISPLAY_WIDTH; i++) {
        display_line_on_display(read_file(SPIFFS, "Line" + String(i + 1)));
      }
    } else {
      tft.fillScreen(0x0000);
      tft.setTextSize(2);
      tft.setTextColor(65535);
      disp_centered_text("No image is set (yet)", 100);
    }
  }
  x = 0;
  y = 0;
  Serial.println("");
  Serial.println("Connecting to Wi-Fi");
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print("#");
  }
  delay(24);
  EEPROM.begin(EEPROM_SIZE);
  for (int i = 0; i < 32; i++) {
    aes_key[i] = EEPROM.read(i);
  }
  //char ipadr[20];
  //sprintf(ipadr, "IP:%s", WiFi.localIP().toString().c_str());
  //disp_centered_text(ipadr, 40);
  /*
  String extr_eeprom_content;
  for (int i = 32; i < 34; i++) {
    if (EEPROM.read(i) < 16)
      extr_eeprom_content += "0";
    extr_eeprom_content += String(EEPROM.read(i), HEX);
  }
  */
  udp_port = (EEPROM.read(32) << 8) | EEPROM.read(33);
  EEPROM.end();
  if (udp.listen(udp_port)) {
    Serial.print("\nUDP Listening on IP: ");
    Serial.println(WiFi.localIP());
    udp.onPacket([](AsyncUDPPacket packet) {
      if (packet.length() == 1) {
        x = 0;
        y = 0;
      } else {
        /*
        for (int i = 0; i < packet.length(); i += 2) {
          tft.drawPixel(x, y, (packet.data()[(i + 1)] << 8) | packet.data()[i]);
          x++;
          if (x == DISPLAY_WIDTH){
            x = 0;
            y++;
          }
        }
        */
        back_key();
        clear_variables();
        int ext = 0;
        decract = -1;
        string_for_data = "";
        for (int i = 0; i < packet.length(); i += 16) { // 656 /16 
          int br = false;
          byte res[16];
          byte prev_res[16];
          for (int j = 0; j < 16; j++) {
            res[j] = packet.data()[j + ext];
          }

          if (decract > 16) {
            for (int j = 0; j < 16; j++) {
              prev_res[j] = packet.data()[j + ext - 16];
            }
          }

          if (br == false) {
            if (decract > 16) {
              for (int i = 0; i < 16; i++) {
                array_for_CBC_mode[i] = prev_res[i];
              }
            }
            uint8_t ret_text[16];
            uint8_t cipher_text[16];
            for (int i = 0; i < 16; i++) {
              cipher_text[i] = res[i];
            }
            uint32_t aes_mode[3] = {
              128,
              192,
              256
            };
            int i = 0;
            aes_context ctx;
            set_aes_key( & ctx, aes_key, aes_mode[m]);
            aes_decrypt_block( & ctx, ret_text, cipher_text);
            incr_aes_key();
            if (decract > 2) {
              for (int i = 0; i < 16; i++) {
                ret_text[i] ^= array_for_CBC_mode[i];
              }

              for (i = 0; i < 16; i += 2) {
                tft.drawPixel(x, y, (ret_text[i + 1] << 8) | ret_text[i]);
                /*
                uint16_t color = (ret_text[i + 1] << 8) | ret_text[i];
                char hexString[5];
                sprintf(hexString, "%04X", color);
                string_for_data += String(hexString);
                */
                if (ret_text[i + 1] < 16)
                  string_for_data += "0";
                string_for_data += String(ret_text[i + 1], HEX);
                if (ret_text[i] < 16)
                  string_for_data += "0";
                string_for_data += String(ret_text[i], HEX);
                x++;
                if (x == DISPLAY_WIDTH) {
                  x = 0;
                  y++;
                }
              }
            }

            if (decract == -1) {
              for (i = 0; i < 16; ++i) {
                array_for_CBC_mode[i] = int(ret_text[i]);
              }
            }
            decract++;
          }
          ext += 16;
          decract += 10;
        }
        rest_key();
        write_to_file_with_overwrite(SPIFFS, "Line" + String(y), string_for_data);
      }
    });
  }
}

void loop() {}
