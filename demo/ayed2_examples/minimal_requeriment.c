#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *next;
} Node;

typedef Node* List;

int main() {
  Node* myNode = (Node*) malloc(sizeof(Node));

  myNode->data = 10;
  myNode->next = NULL;

  Node* myNode2 = (Node*) malloc(sizeof(Node));
  myNode2->data = 22;
  myNode2->next = NULL;

  myNode->next = myNode2;

  return 0;
}
