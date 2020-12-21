struct Base
{
   virtual void foo();
};

struct A : Base
{
   void foo() final;
   virtual void bar();
};

struct B final : A
{
   void bar() override;
};
