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
#include <tclap/CmdLine.h>
#include <sys/resource.h>

int uidSecure(int uid)
{
    const int secureUidMin = 1005;
    const int secureUidMax = 1005; 
    return secureUidMin <= uid && uid <= secureUidMax;
}

class OptionParser
{
public:
    bool Parse( int argc, char **argv );
    std::vector<std::string> GetCmd() { return m_execCmd; }
    std::string GetBotName() { return m_botName; }
    int GetMemoryLimit() { return m_memLimit; }
    int GetUid() { return m_uid; }
    int GetFsizeLimit() { return m_fsizeLimit; }
    std::string GetSandboxDir() { return m_sandboxDir; }
protected:
    std::string m_sandboxDir;
    std::string m_botName;
    int m_memLimit;
    int m_uid;
    int m_fsizeLimit;
    std::vector<std::string> m_execCmd;
};


bool OptionParser::Parse( int argc, char **argv )
{
    try {
        TCLAP::CmdLine cmd("Command description message", ' ', "0.0");
        TCLAP::ValueArg<int> uidArg("u","user-id","Execute as user with uid=UID", 
                                false, 1005, "UID");
        TCLAP::ValueArg<int> memLimitArg("m", "mem-limit", "Limit memory to BYTES bytes", 
                                false, 10000000, "MEM");
        TCLAP::ValueArg<std::string> sandboxDirArg("s", "sandbox-dir", "Chroot to DIR", 
                                false, "sandbox", "DIR");
        TCLAP::ValueArg<std::string> botNameArg("n", "botName", "Use /home/NAME dir for the bot",
                                true, "", "NAME");
        TCLAP::ValueArg<int> fsizeLimitArg("", "fsize-limit", "Set filesize limit to BYTES",
                                false, 1000000, "BYTES");
        TCLAP::UnlabeledMultiArg<std::string> cmdArg("cmd", "command to run", false, "CMD");

        cmd.add(uidArg);
        cmd.add(memLimitArg);
        cmd.add(sandboxDirArg);
        cmd.add(botNameArg);
        cmd.add(fsizeLimitArg);
        cmd.add(cmdArg);

        cmd.parse(argc,argv);

        m_sandboxDir = sandboxDirArg.getValue();
        m_botName = botNameArg.getValue();
        m_uid = uidArg.getValue();
        m_execCmd = cmdArg.getValue();
        m_memLimit = memLimitArg.getValue();
        m_fsizeLimit = fsizeLimitArg.getValue();
    } 
    catch (TCLAP::ArgException &e)  // catch any exceptions
    { 
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl; 
        return false;
    }
    return true;
}

int main(int argc, char **argv)
{
    OptionParser options;
    if ( !options.Parse(argc, argv) )
        return -1;
    
    std::vector<char *> newArgs;
    const std::vector<std::string> &cmd(options.GetCmd());
    for ( int i = 0; i < cmd.size(); i++ )
        newArgs.push_back(strdup(cmd[i].c_str()));
    newArgs.push_back(nullptr);
    
    if ( chroot(options.GetSandboxDir().c_str()) )
    {
        std::cerr << "Can not chroot to " << options.GetSandboxDir() << std::endl;
        return -1;
    }

    std::string homeDir = std::string("/home/") + options.GetBotName();
    if ( chdir(homeDir.c_str()) )
    {
        std::cerr << "Can't chdir to " << homeDir << std::endl;
        return -1;
    }

    int newUid = options.GetUid();
    if ( !uidSecure(newUid) )
    {
        std::cerr << "Uid is not secure: " << newUid << std::endl;
        return -1;
    }

    if ( setuid(newUid) )
    {
        std::cerr << "Can't setuid to " << newUid << std::endl;
        return -1;
    }

    struct rlimit myRlimit;

    myRlimit.rlim_cur = myRlimit.rlim_max = options.GetFsizeLimit();
    setrlimit(RLIMIT_FSIZE, &myRlimit);

    myRlimit.rlim_cur = myRlimit.rlim_max = options.GetMemoryLimit();
    setrlimit(RLIMIT_AS, &myRlimit);

    myRlimit.rlim_cur = myRlimit.rlim_max = 5;
    setrlimit(RLIMIT_NOFILE, &myRlimit);

    std::string newHome = "HOME=" + homeDir;
    std::string newLdPreload = "LD_PRELOAD=/filter.so";
    char newHomeBuf[newHome.length() + 1];
    char newLdPreloadBuf[newLdPreload.length() + 1];
    std::strcpy (newHomeBuf, newHome.c_str());
    std::strcpy (newLdPreloadBuf, newLdPreload.c_str());
    std::vector<char *> newEnv({ newHomeBuf, newLdPreloadBuf, nullptr });
    if ( execvpe(newArgs[0], newArgs.data(), newEnv.data() ) )
    {
        std::cerr << "Couldn't evec " << newArgs[0] << "\n";
        return -1;
    }
    return 0;
}
