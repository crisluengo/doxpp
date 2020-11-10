/** The class A.
 * @T the template parameter T.
 *
 * A longer description of A.
 */
template <typename T>
class A
{
public:
	/** The a function.
	 * @TT the TT template.
	 *
	 * The long description of a.
	 *
	 * @return the value.
	 */
	template <typename TT>
	int a(TT tt);
};

/// A struct where `A` is the template type, not `class A`.
template<typename A, int B = 5>
struct X {
   A member[B];
};
