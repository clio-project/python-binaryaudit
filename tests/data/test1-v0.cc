struct opaque_type;
void
foo(opaque_type*)
{
}
struct opaque_type
{
int member0;
char member1;
};


struct another_type;
void
foo(another_type*)
{
}
struct another_type
{
int member0;
char member1;
};

