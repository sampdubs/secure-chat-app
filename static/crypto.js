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
    
    decrypt(str) {
        return CryptoJS.AES.decrypt(str, this.key != undefined ? this.key.toString() : 'key').toString(CryptoJS.enc.Utf8);
    }
}
