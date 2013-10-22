#include <signal.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>

int uidSecure(int uid)
{
    const int secureUidMin = 1005;
    const int secureUidMax = 1005; 
    return secureUidMin <= uid && uid <= secureUidMax;
}

int main(int argc, char **argv)
{
    const int nMyArgs = 4;
    const int firstNewArg = nMyArgs;

    if ( argc < nMyArgs + 1 )
    {
        std::cerr << "Usage: launcher <uid> <rootdir> <playerName> <executable> [<options>]\n";
        return -1;
    }
    
    std::vector<char *> newArgs(argc - firstNewArg);
    std::copy(argv + firstNewArg, argv + argc, newArgs.begin());
    newArgs.push_back(nullptr);

    if ( chroot(argv[2]) )
    {
        std::cerr << "Can not chroot to " << argv[2] << "\n";
        return -1;
    }

    std::string homeDir = std::string("/home/") + argv[3];
    if ( chdir(homeDir.c_str()) )
    {
        std::cerr << "Can't chdir to " << homeDir << "\n";
        return -1;
    }

    int newUid = atoi(argv[1]);
    if ( !uidSecure(newUid) )
    {
        std::cerr << "Uid is not secure: " << newUid << "\n";
        return -1;
    }
    if ( setuid(newUid) )
    {
        std::cerr << "Can't setuid to " << newUid << "\n";
        return -1;
    }
    
    std::string newHome = "HOME=" + homeDir;
    std::string newLdPreload = "LD_PRELOAD=/filter.so";
    char newHomeBuf[newHome.length() + 1];
    char newLdPreloadBuf[newLdPreload.length() + 1];
    std::strcpy (newHomeBuf, newHome.c_str());
    std::strcpy (newLdPreloadBuf, newLdPreload.c_str());
    std::vector<char *> newEnv({ newHomeBuf, newLdPreloadBuf });
    if ( execvpe(newArgs[0], newArgs.data(), newEnv.data() ) )
    {
        std::cerr << "Couldn't evec " << argv[4] << "\n";
        return -1;
    }
    return 0;
}
