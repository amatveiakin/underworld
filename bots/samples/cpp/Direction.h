enum Direction
{
    DIR_NORTH = 0,
    DIR_SOUTH,
    DIR_EAST,
    DIR_WEST,
    DIR_NUM
};

inline char DirectionToChar( Direction dir )
{
    switch ( dir )
    {
    case DIR_NORTH:
        return 'N';
    case DIR_SOUTH:
        return 'S';
    case DIR_EAST:
        return 'E';
    case DIR_WEST:
        return 'W';
    default:
        assert( false );
    }
}

inline Direction OppositeDirection( Direction dir )
{
    switch ( dir )
    {
    case DIR_NORTH:
        return DIR_SOUTH;
    case DIR_SOUTH:
        return DIR_NORTH;
    case DIR_EAST:
        return DIR_WEST;
    case DIR_WEST:
        return DIR_EAST;
    default:
        assert( false );
    }
}
