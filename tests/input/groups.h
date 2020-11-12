/// \defgroup base A group

/// \addtogroup base

int var1_in_base;

/// \defgroup group1 A sub-group

/// \addtogroup group1

int var1_in_group1;

/// \endgroup

int var2_in_base;

/// \endgroup


/// Some variable
/// \ingroup group1
int var2_in_group1;


/// \defgroup group2 Another sub-group
/// \ingroup base

/// \addtogroup group2

int var1_in_group2;

/// \endgroup


/// \addtogroup base

int var3_in_base;

/// \endgroup
