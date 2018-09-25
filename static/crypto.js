function range(min, max) {
    let output = [];
    for (let i = min; i < max; i++) {
        output.push(i);
    }
    return output;
}

function randPrime(min, n) {
    let a = [false, false].concat(Array(n - 1).fill(true));
    for (let i of range(2, Math.floor(Math.sqrt(n) + 1))) {
        if (a[i]) {
            let k = 0;
            let j = (i + k) * i;
            while (j <= n) {
                a[j] = false;
                k += 1;
                j = (i + k) * i;
            }
        }
    }
    let outlist = [];
    for (let i of range(min, n + 1)) {
        if (a[i]) {
            outlist.push(i);
        }
    }
    return outlist[Math.floor(Math.random() * outlist.length)];
}

class User {
    constructor(p, q) {
        this.p = bigInt(p);
        this.q = bigInt(q);
        this.x = bigInt.randBetween(0, 100000);
        this.a = this.p.pow(this.x).mod(this.q).toJSNumber();
    }
    
    usePrev() {
        this.x = bigInt(this.key);
        this.a = this.p.pow(this.x).mod(this.q).toJSNumber();
    }
    
    calcKey(o) {
        this.o = bigInt(o);
        this.key = this.o.pow(this.x).mod(this.q).toJSNumber();
    }

    encrypt(str) {
        return CryptoJS.AES.encrypt(str + ' ', this.key != undefined ? this.key.toString() : 'key').toString();

    }
    
    decrypt(str){
        return CryptoJS.AES.decrypt(str, this.key != undefined ? this.key.toString() : 'key').toString(CryptoJS.enc.Utf8);
    }
}