struct opaque_type;
void
foo(opaque_type*)
{
}
struct opaque_type
{
char added_member_1;
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
char added_member_2;
int member0;
char member1;
};

