#pragma once
#include <iostream>
#include <istream>
#include <vector>
#include <string>
#include <map>
#include <set>
#include <assert.h>
#include <stdlib.h>
#include "Object.h"
#include "Direction.h"

class Strategy;

class Game
{
public: // constructors & destructors

    // read the initial parameters from the input
    Game( std::istream &input, std::ostream &output );
    ~Game( );

public: // public methods
    void Play( );
    void SetStrategy( Strategy *strategy );

    // interfaces to be used in Strategy
    std::vector< std::vector< Cell > > &Field( )
    {
        return m_field;
    }

    std::vector< Object * > &Objects( )
    {
        return m_objects;
    }

    int Money( )
    {
        return m_money;
    }

    int TurnNo( )
    {
        return m_turnNo;
    }

    int PlayerNo( )
    {
        return m_playerNo;
    }

    int NumPlayers( )
    {
        return m_numPlayers;
    }

    int SizeX( )
    {
        return m_sizeX;
    }

    int SizeY( )
    {
        return m_sizeY;
    }

    void MoveCmd( Object *obj, Direction dir);
    void BuildCmd( int x, int y, ObjType obj);
    void SpawnCmd( Object *obj, Direction dir);

    Cell *GoInDirection( Cell *cell, Direction dir);

public: // static methods
    static void InitStatics( );

protected: // Implementation

    // One turn - put everythong here
    bool DoTurn( );

    // Read the input and create all the objects
    void ReadInput( );

    // Print out our turn
    void PrintOutput( );

    // Do the initialization and the handshake with server
    void Init( );

    // Finalize the turn - clean resources
    void CleanupTurn( );

    // Create and register an object ( called only in ReadInput )
    Object *CreateObj( int x, int y, ObjType type, int owner, int hp );

    // Print the position wo the stderr - for debug purposes
    void PrintPosition( );

protected: // state

    // the 2D field
    std::vector< std::vector< Cell > > m_field;

    // size of the field
    int m_sizeX;
    int m_sizeY;

    // number of players
    int m_numPlayers;

    // number of THE player
    int m_playerNo;

    // the current turn number
    int m_turnNo;

    //
    int m_money;

    // IO streams
    std::istream &m_input;
    std::ostream &m_output;

    // the vector of all objects
    std::vector< Object *> m_objects;

    // the strategy
    Strategy *m_strategy;

protected: // statics
    static std::string handshakeAck;
    static std::map< std::string, ObjType > strToObjType;
    static std::map< ObjType, std::string > objTypeToStr;
};
