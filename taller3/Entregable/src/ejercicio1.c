/*
Realice un programa en C que busque el elemento mayor en cada columna de una matrix
y lo guarde en un vector. La matrix corresponde a 4x3 y está compuesta por enteros (32
bits). Para este programa se desea que todos los números sean positivos para realizar la
comparación. El usuario ingresa todos los números como parámetros y debe imprimir las
tres filas, ası́ como el max_valuesado de cada mayor
*/

#include <emmintrin.h>
#include <immintrin.h>
#include <xmmintrin.h>
#include <smmintrin.h>

#include <stdio.h>
#include "colors.h"

// gcc -o problema2 problema2.c

int main()
{
  //prints variable
  int data;

  // user's inputs
  int input[12];
  bold_yellow();
  printf("\n\nIngrese numeros positivos de la matrix: \n");
  for (int i = 0; i < 12; i++)
  {
    scanf("%d", &input[i]);
  }

  // matrix declaration with user's inputs
  __m128i row0 = _mm_set_epi32(input[3], input[2], input[1], input[0]);
  __m128i row1 = _mm_set_epi32(input[7], input[6], input[5], input[4]);
  __m128i row2 = _mm_set_epi32(input[11], input[10], input[9], input[8]);

  // max_values
  __m128i max_first_two_rows = _mm_max_epi16(row0, row1);
  __m128i max_values = _mm_max_epi16(max_first_two_rows, row2);

  // print matrix
  bold_blue();
  printf("\nLa matrix ingresada fue:\n");
  __m128i matrix[3] = {row0, row1, row2};

  for (int i = 0; i < 3; i++)
  {
    // Convert the pointer to matrix[i] to a pointer to int using the expression (int *)&matrix[i].
    // Then create a row pointer that points to the first 4 bytes of row 'i'.
    int *row = (int *)&matrix[i];
    // 32-bit right shift to extract each int
    printf("%d \t%d \t%d \t%d \t\n", row[0], row[1] >> 32, row[2] >> 32, row[3] >> 32);
  }
  printf("\n");

  // print max_values
  bold_green();
  printf("El valor mayor ingresado de cada columna es:\n");
  // Convert the pointer to matrix[i] to a pointer to int using the expression (int *)&matrix[i].
  // Then create a row pointer that points to the first 4 bytes of row 'i'.
  int *row = (int *)&max_values;
  printf("%d \t%d \t%d \t%d \t\n\n", row[0], row[1] >> 32, row[2] >> 32, row[3] >> 32);
  default_color();
  return 0;
}