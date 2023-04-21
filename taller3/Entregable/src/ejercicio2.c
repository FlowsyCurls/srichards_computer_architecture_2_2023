#include <stdio.h>
#include <immintrin.h>
#include <emmintrin.h>
#include "colors.h"

// Prints
void print_results(__m128i vector, __m128i matrix[], __m128i result)
{
  // print matrix
  bold_blue();
  printf("\nLa matrix es:\n");
  for (int i = 0; i < 4; i++)
  {
    // Convert the pointer to matrix[i] to a pointer to int using the expression (int *)&matrix[i].
    // Then create a row pointer that points to the first 4 bytes of row 'i'.
    int *row = (int *)&matrix[i];
    // 32-bit right shift to extract each int
    printf("%d \t%d \t%d \t%d \t\n", row[0], row[1] >> 32, row[2] >> 32, row[3] >> 32);
  }
  printf("\n");

  // print vector
  bold_magenta();
  printf("El vector es:\n");
  int *row = (int *)&vector;
  printf("%d \t%d \t%d \t%d \t\n", row[0], row[1] >> 32, row[2] >> 32, row[3] >> 32);
  printf("\n");

  // print results
  bold_green();
  printf("El vector resultante es:\n");
  // Convert the pointer to matrix[i] to a pointer to int using the expression (int *)&matrix[i].
  // Then create a row pointer that points to the first 4 bytes of row 'i'.
  row = (int *)&result;
  printf("%d \t%d \t%d \t%d \t\n\n", row[0], row[1] >> 32, row[2] >> 32, row[3] >> 32);
  default_color();
}

int main()
{

  // Vector
  __m128i vector = _mm_set_epi32(3, 2, 1, 0);

  // matrix
  __m128i matrix[4] = {
      _mm_set_epi32(3, 2, 1, 0),
      _mm_set_epi32(7, 6, 5, 4),
      _mm_set_epi32(11, 10, 9, 8),
      _mm_set_epi32(15, 14, 13, 12)};

  // Multiply matrix rows with vector
  __m128i prod[4] = {
      _mm_mullo_epi16(vector, matrix[0]),
      _mm_mullo_epi16(vector, matrix[1]),
      _mm_mullo_epi16(vector, matrix[2]),
      _mm_mullo_epi16(vector, matrix[3])};

  // Sum all rows to get result
  __m128i sum01 = _mm_hadd_epi32(prod[0], prod[1]); // add row 0 y row 1
  __m128i sum23 = _mm_hadd_epi32(prod[2], prod[3]); // add row 2 y row 3
  __m128i result = _mm_hadd_epi32(sum01, sum23);    // result

  // Print results
  print_results(vector, matrix, result);

  return 0;
}


