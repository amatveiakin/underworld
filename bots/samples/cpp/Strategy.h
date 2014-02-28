#pragma once
#include "Game.h"


class Strategy
{
    struct CellData
    {
        int distance;
        bool visited;
    };
public:
    enum GlobalStrategyType
    {
        GS_DEFENCE,
        GS_EXPANSION_FARMS,
        GS_EXPANSION_WARRIORS,
        GS_OFFENCE
    };
public: // constructors & destructors
    Strategy( Game * game ) : m_game( game ) {
        game->SetStrategy( this );
    }
    ~Strategy( );
    void Turn( );
    void Init( );
protected:
    Game *m_game;

    std::vector< Cell *> m_castles;

    // count stuff on the field
    void CalcCounters( );

    // estimate distance from the cell to our castle

    int EstimateRushDist( Cell *cell );

    // caclulate distances from our castle
    //
    void CalcDistance( );

    // Do the initialization of the first turn -
    // analyze the map and castle positions
    void FirstTurnInit( );

    // Make the decisions
    //
    void DecideGlobalStrategy( );

protected: // counters - stats for heuristics

    // m_objCount[ o ][ p ] is the count of objects of type o
    // owned by player p
    std::vector< int > m_objCount[ OBJ_TYPE_NUM ];

    // average rush distance from player's warrior to our castle
    std::vector< int > m_rushDist;

    // cell data for the cells
    std::vector< std::vector< CellData > > m_cellData;

    GlobalStrategyType m_globalStrategy;
};
