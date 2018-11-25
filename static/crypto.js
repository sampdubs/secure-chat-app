// User class for holding numberical information about the client
class User {
    // when a user is initialized
    constructor(p, q) {
        // convert arguments to bigInteger values and keep them as parts of the User instance
        this.p = bigInt(p);
        this.q = bigInt(q);
        // choose a random private x value
        this.x = bigInt.randBetween(0, 50000);
        // calculate the a value and store it as a regular number
        this.a = this.p.pow(this.x).mod(this.q).toJSNumber();
    }

    // calculate they shared private key using another user's a value
    calcKey(o) {
        this.o = bigInt(o);
        this.key = this.o.pow(this.x).mod(this.q).toJSNumber();
    }
    
    // when the client calls the usePrev function on their User instance
    usePrev() {
        // reset the x to be the previous key
        this.x = bigInt(this.key);
        // recalculate the a value (storing as a regular number)
        this.a = this.p.pow(this.x).mod(this.q).toJSNumber();
    }

    // when the client wants to encrypt something
    encrypt(str) {
        // give back aes encrypted of the value to be encrypted, plus a space with the private key. If that's undefined, use the string key
        return CryptoJS.AES.encrypt(str + ' ', this.key != undefined ? this.key.toString() : 'key').toString();
    }
    
    // when the client wants to decrypt something
    decrypt(str) {
        // give back aes decrypted of the value to be decrypted with the private key. If that's undefined, use the string key. Turn it into a string using UTF8
        return CryptoJS.AES.decrypt(str, this.key != undefined ? this.key.toString() : 'key').toString(CryptoJS.enc.Utf8);
    }
}
