#include <string>
#include <list>

/**
 * Foo method.
 */
std::list<std::string> foo();

template <typename T>
struct WithInner {
    using Type = T;
};

using WithInnerIntType = std::list<WithInner<int>::Type>;
