namespace N {
struct A {
   int a;
   int b;
   double c;
   char d;
};
constexpr double foo = 0.1;
void func (
   A const& x = {0, 4, 3.14, 'x'},
   double y = N::foo
);
};
