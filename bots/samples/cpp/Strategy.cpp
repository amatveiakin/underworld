#include "Strategy.h"
#include <queue>

void Strategy::CalcCounters( )
{
    // init counters with zeros
    for ( int objType = 0; objType < OBJ_TYPE_NUM; objType++)
    {
        std::fill( m_objCount[ objType ].begin( ), m_objCount[ objType ].end( ), 0 );
    }

    if ( m_game->TurnNo( ) == 0 )
    {
        FirstTurnInit( );
    }

    std::fill( m_rushDist.begin( ), m_rushDist.end( ), 0 );

    // count objects
    for ( std::vector< Object *>::iterator it = m_game->Objects( ).begin( );
        it != m_game->Objects( ).end( ); it++ )
    {
        Object *obj = *it;
        if ( obj->GetOwner( ) >= 0 )
        {
            m_objCount[ obj->GetType( ) ][ obj->GetOwner( ) ]++;
            if ( obj->GetType( ) == OBJ_WARRIOR )
                m_rushDist[ obj->GetOwner( ) ] += EstimateRushDist( obj->GetCell( ) );
        }
    }

    // average the rush distance
    for ( int p = 0; p < m_game->NumPlayers( ); p++ )
    {
        if ( m_objCount[ OBJ_WARRIOR ][ p ] > 0 )
            m_rushDist[ p ] /= m_objCount[ OBJ_WARRIOR ][ p ];
    }
}

void Strategy::Init( )
{
    for ( int objType = 0; objType < OBJ_TYPE_NUM; objType++ )
        m_objCount[ objType ].resize( m_game->NumPlayers( ) );
    m_rushDist.resize( m_game->NumPlayers( ) );
    m_castles.resize( m_game->NumPlayers( ) );
    m_cellData.resize( m_game->SizeY( ) );
    for ( int y = 0; y < m_game->SizeY( ); y++ )
        m_cellData[ y ].resize( m_game->SizeX( ) );
}

void Strategy::FirstTurnInit( )
{
    // detect castles
    for ( std::vector< Object *>::iterator it = m_game->Objects( ).begin( );
        it != m_game->Objects( ).end( ); it++ )
    {
        Object *obj = *it;
        if ( obj->GetOwner( ) >= 0 && obj->GetType( ) == OBJ_CASTLE )
        {
            m_castles[ obj->GetOwner( ) ] = obj->GetCell( );
        }
    }
    CalcDistance( );
}

// calculate distance from our castle to all the cells using BFS
//
void Strategy::CalcDistance( )
{
    std::queue< Cell * > q;
    Cell *castle = m_castles[ m_game->PlayerNo( ) ];
    q.push( castle );
    m_cellData[ castle->y ][ castle->x ].visited = true;
    while ( !q.empty( ) )
    {
        Cell *curCell = q.front( );
        q.pop( );
        for ( int dir = 0; dir < DIR_NUM; dir++)
        {
            Cell *nextCell = m_game->GoInDirection( curCell, Direction( dir ) );
            CellData *curData = &m_cellData[ curCell->y ][ curCell->x ];
            if ( nextCell &&
                 ( !nextCell->objRef || nextCell->objRef->GetType( ) != OBJ_WALL ) )
            {
                CellData *nextData = &m_cellData[ nextCell->y ][ nextCell->x ];
                if ( !nextData->visited )
                {
                    nextData->visited = true;
                    nextData->distance = curData->distance + 1;
                    q.push( nextCell );
                }
            }
        }
    }
}

int Strategy::EstimateRushDist( Cell *cell )
{
    return m_cellData[ cell->y][ cell->x ].distance;
}

void Strategy::DecideGlobalStrategy( )
{
    // TODO: add more magic constants into the code
    //
    int myIncome = m_objCount[ OBJ_FARM ][ m_game->PlayerNo( ) ] * 50;
    int myPower = m_objCount[ OBJ_WARRIOR ][ m_game->PlayerNo( ) ];
    bool notTheBestIncome = false, notTheStrongestArmy = false;
    for ( int p = 0; p < m_game->NumPlayers( ); p++ )
        if ( p != m_game->PlayerNo( ) )
        {
            // Enemy's power
            int hisPower = m_objCount[ OBJ_WARRIOR ][ p ];
            // Estimate our power when the enemy arrives
            int relPower = myPower + myIncome * m_rushDist[ p ] / 2;
            if ( relPower < hisPower )
            {
                m_globalStrategy = GS_DEFENCE;
                return ;
            }
            int hisIncome = m_objCount[ OBJ_FARM ][ p ] * 50;
            if ( hisIncome >= myIncome )
            {
                notTheBestIncome = true;
            }
            if ( hisPower >= myPower )
            {
                notTheStrongestArmy = true;
            }
        }
    if ( notTheBestIncome )
    {
        m_globalStrategy = GS_EXPANSION_FARMS;
        return;
    }
    if ( notTheStrongestArmy )
    {
        m_globalStrategy = GS_EXPANSION_WARRIORS;
        return;
    }
    m_globalStrategy = GS_OFFENCE;
}

Strategy::~Strategy( )
{
}

void Strategy::Turn( )
{
    CalcCounters( );
    DecideGlobalStrategy( );
    for ( std::vector< Object * >::iterator it = m_game->Objects( ).begin( );
        it != m_game->Objects( ).end( ); it++ )
    {
        Object *obj = *it;
        if ( obj->GetOwner( ) != m_game->PlayerNo( ) )
            continue;
        switch ( obj->GetType( ) )
        {
        case OBJ_BARRACKS:
            // build army for offence or defence
            if ( m_globalStrategy == GS_OFFENCE || m_globalStrategy == GS_DEFENCE
                    || m_globalStrategy == GS_EXPANSION_WARRIORS )
            {
                for ( int i = 0; i < DIR_NUM; i++ )
                {
                    Cell *nbr = m_game->GoInDirection( obj->GetCell( ), Direction( i ) );
                    if ( !nbr )
                        continue;
                    if ( !nbr->objRef )
                    {
                        // free neighbour found
                        m_game->SpawnCmd( obj, Direction( i ) );
                    }
                }
            }
            break;
        case OBJ_WARRIOR: {
            int maxDir = -1, minDir = -1;
            int myDist = m_cellData[ obj->GetCell( )->y ][ obj->GetCell( )->x ].distance;
            int maxDist = myDist;
            int minDist = myDist;
            for ( int i = 0; i < DIR_NUM; i++ )
            {
                Cell *nbr = m_game->GoInDirection( obj->GetCell( ), Direction( i ) );
                if ( !nbr )
                    continue;
                if ( !nbr->objRef || nbr->objRef->GetType( ) == OBJ_WARRIOR )
                {
                    int nbrDist = m_cellData[ nbr->y ][ nbr->x ].distance;
                    if ( nbrDist < minDist ||
                        ( nbrDist == minDist && ( rand( ) & 1 ) ) )
                    {
                        minDist = nbrDist;
                        minDir = i;
                    }
                    if ( nbrDist > maxDist ||
                        ( nbrDist == maxDist && ( rand( ) & 1 ) ) )
                    {
                        maxDist = nbrDist;
                        maxDir = i;
                    }
                }
            }
            if ( m_globalStrategy == GS_DEFENCE  && ( myDist > 5 || m_game->Money( ) < 500 ) )
            {
                if ( minDir != -1 )
                    m_game->MoveCmd( obj, Direction( minDir ) );
            } else {
                if ( ( m_globalStrategy == GS_OFFENCE || myDist < 5 ) && maxDir != -1 )
                    m_game->MoveCmd( obj, Direction( maxDir ) );
            }
            break;
            }
        default:
            break;
        }
    }
    if ( m_globalStrategy == GS_EXPANSION_FARMS  && m_game->Money( ) >= 1000 )
    {
        // try to build a farm
        std::vector< Cell * > buildList;
        for ( std::vector< Object *>::iterator it = m_game->Objects( ).begin( );
            it != m_game->Objects( ).end( ); it++ )

        {
            Object *obj = *it;
            if ( obj->GetOwner( ) != m_game->PlayerNo( ) )
                continue;
            if ( obj->GetType( ) == OBJ_WARRIOR  ||
                 obj->GetType( ) == OBJ_BARRACKS )
                continue;

            Cell *cell = obj->GetCell( );
            Cell *newCell = NULL;
            for ( int i = 0; i < DIR_NUM; i++ )
            {
                newCell = m_game->GoInDirection( cell, Direction( i ) );
                if ( !newCell )
                    continue;
                newCell = m_game->GoInDirection( newCell, Direction( i ) );
                if ( !newCell )
                    continue;
                if ( !newCell->objRef )
                    buildList.push_back( newCell );
            }
        }

        if ( buildList.size( ) != 0 )
        {
            int randomIndex = rand( ) % buildList.size( );
            Cell *buildCell = buildList[ randomIndex ];
            m_game->BuildCmd( buildCell->x, buildCell->y, OBJ_FARM );
        }
    }
}
