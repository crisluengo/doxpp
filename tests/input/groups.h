/// \group base A group
/// \addtogroup

int var1_in_base;

/// \defgroup group1 A sub-group
/// \addtogroup

int var1_in_group1;

/// \endgroup

int var2_in_base;

/// \endgroup


/// Some variable
/// \ingroup group1
int var2_in_group1;


/// \group group2 Another sub-group
/// \ingroup base
/// \addtogroup

int var1_in_group2;

/// \endgroup


/// \addtogroup base

int var3_in_base;

/// \endgroup
