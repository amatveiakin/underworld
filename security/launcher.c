#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#define MAX_CMD_ARGS 20
#define BUF_LEN 4096

int uidSecure(int uid)
{
    const int secureUidMin = 1005;
    const int secureUidMax = 1005; 
    return secureUidMin <= uid && uid <= secureUidMax;
}

int main(int argc, char **argv)
{
    char *tok[MAX_CMD_ARGS];
    char buf[BUF_LEN], buf2[BUF_LEN], buf3[BUF_LEN];
    char *newEnv[] = { buf2, buf3, NULL };
    const char * homedir = "/home/";
    int i = 0, j = 4;

    if ( argc < 5 )
    {
        fprintf(stderr, "Usage: launcher <uid> <rootdir> <playerName> <executable> [options>]");
        return -1;
    }
    
    while ( i < MAX_CMD_ARGS - 1 && j < argc )
    {
        tok[ i++ ] = argv[ j++ ];
    }
    tok[ i ] = NULL;

    if ( chroot(argv[2]) )
    {
        fprintf(stderr, "Can not chroot to %s\n", argv[2]);
        return -1;
    }

    strncpy(buf, homedir, BUF_LEN - 1);
    strncat(buf, argv[3], BUF_LEN - strlen(homedir) - 1);
    snprintf(buf2, BUF_LEN, "HOME=%s", buf);
    buf2[BUF_LEN - 1] = '\0';
    snprintf(buf3, BUF_LEN, "LD_PRELOAD=/filter.so");
    buf3[BUF_LEN - 1] = '\0';
    if ( chdir(buf) )
    {
        fprintf(stderr, "Can't chdir to %s\n", buf);
        return -1;
    }

    int newUid = atoi(argv[1]);
    if ( !uidSecure(newUid) )
    {
        fprintf(stderr, "Uid is not secure: %d\n", newUid);
        return -1;
    }
    if ( setuid(newUid) )
    {
        fprintf(stderr, "Can't setuid to %d\n", newUid);
        return -1;
    }
    
    if ( execve(tok[0], tok, newEnv) )
    {
        fprintf(stderr, "Couldn't evec %s\n", argv[4]);
        return -1;
    }
    return 0;
}
