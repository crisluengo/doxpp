/** The struct A.
 *
 * A longer description of A.
 */
struct A
{
	int I;
	float F;
};

/// A "constructor" function
/// \relates A
A    *a_new  (void);
/// A "destructor" function
/// \relates A
void  a_free (A *a);

/// A "getter" function
/// \relates A
int   a_i (A *a);
/// Another "getter" function
/// \relates A
float a_f (A *a);
