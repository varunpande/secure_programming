// used as a wrapper to invoke a set-UID root python process
#include <unistd.h>

void main(int argc, char **argv){
    execve("./assignment.py", argv, NULL);
}