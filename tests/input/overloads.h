class AClass{
   /// A member
   int member;
   /// Another member
   float array[5];

public:
   /// Overloaded constructor 1
   AClass(double x[], int y);
   /// Overloaded constructor 2
   AClass(double const x[], int y);
   /// Copy constructor
   AClass(const AClass &) = default;
   /// Move constructor
   AClass(AClass &&) = default;
   /// Destructor
   ~AClass();
   /// Copy assignment
   AClass& operator=(const AClass &) = default;
   /// Move assignment
   AClass& operator=(AClass &&) = default;
};
