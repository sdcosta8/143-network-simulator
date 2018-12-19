import main

print("Starting test 0!")

main.run_simulation('test0_FAST.json')

main.run_simulation('test0_RENO.json')

print("Starting test1!")

main.run_simulation('test1_FAST.json')

main.run_simulation('test1_RENO.json')

print("Starting test2!")

main.run_simulation('test2_FAST.json')

main.run_simulation('test2_RENO.json')

print("Starting test3!")

main.run_simulation('test3.json')

print("Starting test4!")

main.run_simulation('test4.json')

print("Starting test5!")

main.run_simulation('test5_FAST.json')

main.run_simulation('test5_RENO.json')

print("Starting extra test case with link switching!")

main.run_simulation('extra_test_RENO.json')

main.run_simulation('extra_test_FAST.json')

print("Starting extra test case without link switching!")

main.run_simulation('extra_test_no_switching_RENO.json')

main.run_simulation('extra_test_no_switching_FAST.json')
