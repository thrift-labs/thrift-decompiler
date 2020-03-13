include "bob.thrift"

namespace go alice_thrift
namespace py alice_thrift
namespace java alice_thrift

typedef i32 int

service AliceService
{
    int multiply(1:int n1, 2:int n2),
}
