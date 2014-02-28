#include <iostream>
#include <istream>
#include <vector>
#include <string>
#include <map>
#include <set>
#include <assert.h>
#include <stdlib.h>

#include "Game.h"
#include "Strategy.h"


int main( int argc, char **argv )
{
    Game::InitStatics( );
    Game g( std::cin, std::cout );
    Strategy s( &g);
    g.Play( );
    return 0;
}
