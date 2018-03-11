# cython-npm
Cython project management like npm in nodejs. This project is inspired by npm in nodejs.

### Installation

You can easily install by:
```
pip install cython-npm
```

### What problems does it solve ?
When using cython, we face the problem of compile cython file. We can do it easily by:
```
import pyximport; pyximport.install()
```
But that it is not recommended to let **pyximport** build code on end user side as it *hooks into their import system*. The best way to cater for end users is to provide pre-built binary packages.
So this project compiles .pyx file and provides pre-built binary packages for easy of use.

### Quickstart:
Basic use to Complie file or folder
``` 
from cython_npm.cythoncompile import export
export('examplefile.pyx')
export('./examplefolder')
# then import them to use
import examplefile
from examplefolder import *
```
You should do this code once time only.

### Create install file like package.json
You can also compile many files or folders at once time. Create a file name `install.py` in the root of your project/package and write the code below:
```
from cython_npm.cythoncompile import install
Manymodules = [
    # put your modules list here
    examplefile.pyx,
    ./examplefolder
]
install(Manymodules)
```
Run the file before start your project
```
python install.py
```
Or add first line `import install` in startup file of your project. Use install or export in parent folder will compile all .pyx file in subdirectories.
### Using require('path') as nodejs
You can also relative or fullpath import in python by `require` function. For example:
```
from cython_npm.cythoncompile import require

# import .pyx file. Will cause error if it is not compiled by export() yet. 
# Default value of recompile is True, only apply for .py file. To import .pyx, change recompile=False
examplefile = require('../parentpackage', recompile=False) # import cython package from parent folder
examplefile.somefunction()

# it also support relative import .py file
examplefile = require('../parentpackage')
examplefile.somefunction()
```

Using requirepyx('path'): `requirepyx` is simillar to `require` except:
* Use for cython file ('.pyx') only
* Equivalent to export('.pyx file') and require('.pyx file')
Example:
```
from cython_npm.cythoncompile import export
export('examplefile')
require('examplefile',recompile=False)
# The code above is the same as:
from cython_npm.cythoncompile import requirepyx
requirepyx('examplefile')
```

### Example: Cython vs speed test battle
This example compare the speed between cython vs python, Swift, Go and Code differences in doing a short calculation. Cython_npm is used in the test. This test is forked from 'marcinkliks', the original code and test is here: 
[Swift vs Go vs Python battle](http://www.marcinkliks.pl/2015/02/22/swift-vs-others/). Note: We use Swift and Go test results as pattern and do not retest them. Go to see in test folder in github for more examples

Testing condition:
* Python version: Python 3.6.3 :: Anaconda, Inc.

* About computer: MacBook Pro (13-inch, 2016, Two Thunderbolt 3 ports), 2 GHz Intel Core i5, 256GB SSD

Hypothesis:  
* Is Cython really fast (compare to other language) ? 
* How does Code differences affect performance ?

#### Test process and results as shown below:
0. Recall the speed of Swift: 0m0.416s, Go: 0m0.592s and Pypy: 0m2.633s

1. Test pure python code:
    ```
    sum = 0

    for e in range(30):
        sum = 0
        x = []

        for i in range(1000000):
            x.append(i)

        y = []
        for i in range(1000000 - 1):
            y.append(x[i] + x[i+1])

        i = 0
        for i in range(0, 1000000, 100):
            sum += y[i]

    print(sum)
    ```
    Speed test result is same/similar to original test
    ```
    time python test_python.py
    9999010000

    real    0m12.825s
    user    0m11.721s
    sys     0m1.061s
    ```
2. Test cython code: Create run.py with code: 
    ```
    from cython_npm.cythoncompile import export
    export('test_cython.pyx') # will do once time
    import test_cython
    ```
    Code in __test_cython.pyx__:
    ```
    cdef long sum = 0
    cdef int i
    cdef int e
    for e in range(30):
        sum = 0
        x = []

        for i in range(1000000):
            x.append(i)

        y = []
        for i in range(1000000 - 1):
            y.append(x[i] + x[i+1])

        i = 0
        for i in range(0, 1000000, 100):
            sum += y[i]

    print(sum)
    ```
    Speed test result: time python run.py
    ```
    time python run.py
    9999010000

    real    0m5.803s
    user    0m4.496s
    sys     0m1.211s
    ```
3. Test cython code with list optimization and cache: create similar run.py. Code in __test_cythoncache.pyx__:
    ```
    from functools import lru_cache
    @lru_cache(maxsize=128)
    def dotest():
        cdef long mysum = 0
        cdef int i
        cdef int e
        for e in range(30):
            mysum = 0
            x = [i for i in range(1000000)]

            y = [x[i] + x[i+1] for i in range(1000000-1)]

            i = 0
            for i in range(0, 1000000, 100):
                mysum += y[i]

        print(mysum)
    dotest()
    ```
    Speed test result:
    ```
    time python run.py
    9999010000

    real    0m3.373s
    user    0m2.360s
    sys     0m1.001s
    ```
4. Test cython code with cache and C array: create similar run.py. Code in **test_cythoncache.pyx**:
    ```
    from functools import lru_cache
    @lru_cache(maxsize=128)
    def dotest():
        cdef long mysum = 0
        cdef int i
        cdef int e
        cdef int x[1000000]
        cdef int y[1000000]
        for e in range(30):
            mysum = 0
            for i in range(1000000):
                x[i] = i

            # y = []
            for i in range(1000000 - 1):
                y[i] = (x[i] + x[i+1])

            i = 0
            for i in range(0, 1000000, 100):
                mysum += y[i]

        print(mysum)
    dotest()
    ```
    Speed test result:
    ```
    time python run.py
    9999010000

    real    0m0.085s
    user    0m0.067s
    sys     0m0.015s
    ```

#### Conclusions
* With a slight change, Cython make pure python code faster by 2X time. But it is very slow compare to Swift and Go
* Appling some optimal technical, Cython make python nearly 4X time faster than the original code. It may be the acceptable result. Pypy result seems very attractive too.
* Using C array, Cython make the code become very fast. It consumes only 0.085s to complete as 4X time faster than Swift, 6X time faster than Go. It maybe the fastest but it is unusable in real life. 
* After all, i wish cython and cython_npm could give you more usefull options in coding




