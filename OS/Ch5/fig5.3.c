#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

int main(int argc, char *argv[]) {
    printf("Hello world (pid:%d)\n", (int) getpid());
    int rc = fork();
    if (rc < 0) {
        fprintf(stderr, "Fork failed\n");
        exit(1);
    }
    else if (rc == 0) {
        printf("Child process running (pid:%d)\n", (int) getpid());
        char *args[3];
        args[0] = strdup("wc");
        args[1] = strdup("fig5.3.c");
        args[2] = NULL;
        execvp(args[0], args);
        printf("No No No Noooooo! This line shouldn't have printed out. Who the hell coded this thing? Stupid!");
    }
    else {
        int wc = wait(NULL);
        printf("Parent process of %d running (wc:%d) (pid:%d)\n", rc, wc, (int) getpid());
    }
}