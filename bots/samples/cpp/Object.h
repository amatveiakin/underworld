#pragma once

#include "Cell.h"

enum ObjType
{
    OBJ_NONE=0,
    OBJ_BARRACKS,
    OBJ_CASTLE,
    OBJ_FARM,
    OBJ_WALL,
    OBJ_WARRIOR,
    OBJ_TYPE_NUM
};

class Object
{
public: // constructors & destructors
    Object( Cell *cell, ObjType type, int owner, int hp ):
        m_cell( cell ), m_type( type ), m_owner( owner ), m_hp( hp )
    {
        // link to the cell
        assert( cell->objRef == NULL );
        cell->objRef = this;
    }
    ~Object( )
    {
        // unlink from the cell
        m_cell->objRef = NULL;
    }
public: // public methods
    Cell *GetCell( )
    {
        return m_cell;
    }

    int GetHp( )
    {
        return m_hp;
    }

    int GetOwner( )
    {
        return m_owner;
    }

    ObjType GetType( )
    {
        return m_type;
    }

protected: // state
    Cell *m_cell;
    int m_owner;
    int m_hp;
    ObjType m_type;
};
