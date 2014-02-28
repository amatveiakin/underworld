#include "Game.h"
#include "Strategy.h"
#include <time.h>

std::string Game::handshakeAck;
std::map< std::string, ObjType > Game::strToObjType;
std::map< ObjType, std::string > Game::objTypeToStr;

void Game::InitStatics( )
{
    handshakeAck = "crayfish";
    strToObjType["W"] = OBJ_WARRIOR;
    strToObjType["C"] = OBJ_CASTLE;
    strToObjType["B"] = OBJ_BARRACKS;
    strToObjType["F"] = OBJ_FARM;
    strToObjType["#"] = OBJ_WALL;

    // invert the map
    for ( std::map< std::string, ObjType >::iterator it = strToObjType.begin( );
            it != strToObjType.end( ); it++)
    {
        objTypeToStr[it->second] = it->first;
    }
}
Game::Game( std::istream &input, std::ostream &output )
    : m_input( input ), m_output( output ), m_turnNo( 0 )
{
}

void Game::Init( )
{
    // rand init
    srand(time(NULL));
    // perform the handshake
    std::string handshakeSyn;
    std::getline( m_input, handshakeSyn );
    m_output << handshakeAck << "\n";

    // read the initial parameters
    m_input >> m_sizeX >> m_sizeY >> m_numPlayers >> m_playerNo;
    m_field.resize( m_sizeY );

    // prepare the field
    for ( int i = 0; i < m_sizeY; i++)
    {
        m_field[i].resize(m_sizeX);
        for ( int j = 0; j < m_sizeX; j++ )
        {
            m_field[i][j].x = j;
            m_field[i][j].y = i;
            m_field[i][j].objRef = NULL;
        }
    }
    m_strategy->Init( );
}

void Game::ReadInput( )
{
    std::string str;

    m_input >> str;
    while ( str.compare("end") )
    {
        if ( !str.compare("money") )
            m_input >> m_money >> str;
        else
        {
            int objX, objY, objOwner, objHp = -1;
            std::string objTypeStr;
            ObjType objType;

            objX = atoi( str.c_str( ) );
            m_input >> objY >> objOwner >> objTypeStr >> objHp >> str;
            objType = strToObjType[objTypeStr];

            CreateObj( objX, objY, objType, objOwner, objHp );
        }
    }
}

void Game::PrintOutput( )
{
    m_strategy->Turn( );
    std::cout << "end\n";
}

Object *Game::CreateObj( int x, int y, ObjType type, int owner, int hp )
{
    Object *newObj = new Object( &m_field[y][x], type, owner, hp);
    m_objects.push_back( newObj );
    return newObj;
}

void Game::CleanupTurn( )
{
    for ( std::vector< Object *>::iterator it = m_objects.begin( );
             it != m_objects.end( ); it++)
    {
        delete (*it);
    }
    m_objects.clear( );
}

Game::~Game( )
{
}

bool Game::DoTurn( )
{
    ReadInput( );
    PrintOutput( );
    CleanupTurn( );
    m_turnNo += 1;
    return true;
}

void Game::Play( )
{
    Init( );
    while ( DoTurn( ) );
}

void Game::PrintPosition( )
{
    for ( int i = 0; i < m_sizeY; i++ )
    {
        for ( int j = 0; j < m_sizeX; j++ )
        {
            Object *obj = m_field[i][j].objRef;
            if ( obj )
            {
                std::string s = objTypeToStr[ obj->GetType( ) ];
                if ( obj->GetOwner( ) != m_playerNo )
                    s[ 0 ] = tolower( s[0] );
                std::cerr << s;
            }
            else
            {
                std::cerr << " ";
            }
        }
        std::cerr << "\n";
    }
}

void Game::MoveCmd( Object *obj, Direction dir )
{
    assert( obj->GetType( ) == OBJ_WARRIOR );
    m_output << "move " << obj->GetCell( )->x << " " <<
        obj->GetCell( )->y << " " << DirectionToChar( dir ) << "\n";
}

void Game::SpawnCmd( Object *obj, Direction dir )
{
    assert( obj->GetType( ) == OBJ_BARRACKS );
    m_output << "spawn " << obj->GetCell( )->x << " " <<
        obj->GetCell( )->y << " " << DirectionToChar( dir ) << "\n";
}

void Game::BuildCmd( int x, int y, ObjType objType )
{
    m_output << "build " << x << " " << y << " " <<
        objTypeToStr[ objType ] << "\n";
}

void Game::SetStrategy( Strategy *strategy )
{
    m_strategy = strategy;
}

Cell *Game::GoInDirection( Cell *cell, Direction dir )
{
    int newX = cell->x, newY = cell->y;
    switch ( dir )
    {
        case DIR_EAST:
            newX++;
            break;
        case DIR_WEST:
            newX--;
            break;
        case DIR_SOUTH:
            newY++;
            break;
        case DIR_NORTH:
            newY--;
            break;
        default:
            assert( false );
    }
    if ( newX < 0 || newX >= m_sizeX || newY < 0 || newY >= m_sizeY )
        return NULL;
    return &m_field[ newY ][ newX ];
}
