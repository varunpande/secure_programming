########################################################################################
Name: Varunkumar Pande
My-Mav: 1001722538
########################################################################################

Environment setup:
1. The python program is compatible with python versions ranging from 2.7.5 - 3.8.6.

2. A GCC compiler is needed to compile the callee.c program.

*Compile instruction: gcc -o callee callee.c

3. You need to make the "callee" compiled file obtained from above step a SET-UID root.

*Instructions to make it setuid:
chown root callee
chmod 4755 callee 

4. Run the program by simply calling the above compiled file.
eg: ./callee LIST
eg: ./callee ADD <name> <number>
eg: ./callee DEL <name or number>