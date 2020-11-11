class A
{
public:
	/** A function of A.
	 * @a the argument.
	 *
	 * A longer description of f. Use `a` to pass \ref A.
	 *
	 * @returns a number.
	 */
	int f(A* a);

	/** A const function of A. */
   int f(A* a) const;

	/** A static function of A. */
   int s(A& a);
};
