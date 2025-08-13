#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to demonstrate nested loops and conditions
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Function with multiple branching paths
int grade_calculator(int score) {
    char grade;

    if (score >= 90) {
        grade = 'A';
        printf("Excellent work!\n");
    } else if (score >= 80) {
        grade = 'B';
        printf("Good job!\n");
    } else if (score >= 70) {
        grade = 'C';
        printf("Average performance.\n");
    } else if (score >= 60) {
        grade = 'D';
        printf("Below average.\n");
    } else {
        grade = 'F';
        printf("Failing grade.\n");
    }

    return grade;
}

// Function with loops and nested conditions
void array_processor(int *arr, int size) {
    int sum = 0;
    int max = arr[0];
    int min = arr[0];

    for (int i = 0; i < size; i++) {
        sum += arr[i];

        if (arr[i] > max) {
            max = arr[i];
        }

        if (arr[i] < min) {
            min = arr[i];
        }

        // Process even numbers differently
        if (arr[i] % 2 == 0) {
            printf("Even number found: %d\n", arr[i]);
        } else {
            printf("Odd number found: %d\n", arr[i]);
        }
    }

    printf("Sum: %d, Max: %d, Min: %d\n", sum, max, min);
}

// Function with switch statement
void menu_handler(int choice) {
    switch (choice) {
        case 1:
            printf("Opening file...\n");
            break;
        case 2:
            printf("Saving file...\n");
            break;
        case 3:
            printf("Printing document...\n");
            break;
        case 4:
            printf("Exiting program...\n");
            exit(0);
        default:
            printf("Invalid choice. Please try again.\n");
            break;
    }
}

// Function with while loop and complex logic
int string_analyzer(const char *str) {
    int length = strlen(str);
    int vowels = 0;
    int consonants = 0;
    int digits = 0;
    int i = 0;

    while (i < length) {
        char c = str[i];

        if (c >= '0' && c <= '9') {
            digits++;
        } else if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
                c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
                vowels++;
                } else {
                    consonants++;
                }
        }
        i++;
    }

    printf("Analysis of '%s':\n", str);
    printf("Length: %d\n", length);
    printf("Vowels: %d\n", vowels);
    printf("Consonants: %d\n", consonants);
    printf("Digits: %d\n", digits);

    return vowels + consonants + digits;
}

// Main function with multiple function calls and control structures
int main() {
    printf("=== Control Flow Flattening Demo ===\n\n");

    // Test fibonacci function
    printf("Fibonacci sequence (first 10 numbers):\n");
    for (int i = 0; i < 10; i++) {
        printf("%d ", fibonacci(i));
    }
    printf("\n\n");

    // Test grade calculator
    printf("Grade calculations:\n");
    int scores[] = {95, 87, 76, 65, 45};
    for (int i = 0; i < 5; i++) {
        printf("Score %d gets grade: %c\n", scores[i], grade_calculator(scores[i]));
    }
    printf("\n");

    // Test array processor
    printf("Array processing:\n");
    int test_array[] = {10, 25, 3, 47, 8, 91, 2, 36};
    int array_size = sizeof(test_array) / sizeof(test_array[0]);
    array_processor(test_array, array_size);
    printf("\n");

    // Test string analyzer
    printf("String analysis:\n");
    string_analyzer("Hello World 123");
    printf("\n");

    // Test menu handler
    printf("Menu simulation:\n");
    menu_handler(1);
    menu_handler(3);
    menu_handler(99);

    printf("\nProgram completed successfully!\n");
    return 0;
}
