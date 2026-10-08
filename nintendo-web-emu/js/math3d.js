// 3D Matrix and Vector Math Utilities for Switch Maxwell and N64 Fast3D
const Mat4 = {
    identity() {
        const out = new Float32Array(16);
        out[0] = 1; out[5] = 1; out[10] = 1; out[15] = 1;
        return out;
    },

    perspective(fovyRad, aspect, near, far) {
        const out = new Float32Array(16);
        const f = 1.0 / Math.tan(fovyRad / 2);
        const nf = 1 / (near - far);
        out[0] = f / aspect;
        out[5] = f;
        out[10] = (far + near) * nf;
        out[11] = -1;
        out[14] = 2 * far * near * nf;
        return out;
    },

    lookAt(eye, center, up) {
        const out = new Float32Array(16);
        let z0 = eye[0] - center[0], z1 = eye[1] - center[1], z2 = eye[2] - center[2];
        let len = 1 / Math.hypot(z0, z1, z2);
        z0 *= len; z1 *= len; z2 *= len;

        let x0 = up[1] * z2 - up[2] * z1, x1 = up[2] * z0 - up[0] * z2, x2 = up[0] * z1 - up[1] * z0;
        len = Math.hypot(x0, x1, x2);
        if (!len) { x0 = 0; x1 = 0; x2 = 0; } else { len = 1 / len; x0 *= len; x1 *= len; x2 *= len; }

        let y0 = z1 * x2 - z2 * x1, y1 = z2 * x0 - z0 * x2, y2 = z0 * x1 - z1 * x0;
        len = Math.hypot(y0, y1, y2);
        if (!len) { y0 = 0; y1 = 0; y2 = 0; } else { len = 1 / len; y0 *= len; y1 *= len; y2 *= len; }

        out[0] = x0; out[1] = y0; out[2] = z0; out[3] = 0;
        out[4] = x1; out[5] = y1; out[6] = z1; out[7] = 0;
        out[8] = x2; out[9] = y2; out[10] = z2; out[11] = 0;
        out[12] = -(x0 * eye[0] + x1 * eye[1] + x2 * eye[2]);
        out[13] = -(y0 * eye[0] + y1 * eye[1] + y2 * eye[2]);
        out[14] = -(z0 * eye[0] + z1 * eye[1] + z2 * eye[2]);
        out[15] = 1;
        return out;
    },

    multiply(a, b) {
        const out = new Float32Array(16);
        for (let i = 0; i < 4; ++i) {
            for (let j = 0; j < 4; ++j) {
                out[j * 4 + i] = 
                    a[i]      * b[j * 4] +
                    a[i + 4]  * b[j * 4 + 1] +
                    a[i + 8]  * b[j * 4 + 2] +
                    a[i + 12] * b[j * 4 + 3];
            }
        }
        return out;
    },

    rotateX(m, rad) {
        const c = Math.cos(rad), s = Math.sin(rad);
        const rot = Mat4.identity();
        rot[5] = c; rot[6] = s;
        rot[9] = -s; rot[10] = c;
        return Mat4.multiply(m, rot);
    },

    rotateY(m, rad) {
        const c = Math.cos(rad), s = Math.sin(rad);
        const rot = Mat4.identity();
        rot[0] = c; rot[2] = -s;
        rot[8] = s; rot[10] = c;
        return Mat4.multiply(m, rot);
    },

    rotateZ(m, rad) {
        const c = Math.cos(rad), s = Math.sin(rad);
        const rot = Mat4.identity();
        rot[0] = c; rot[1] = s;
        rot[4] = -s; rot[5] = c;
        return Mat4.multiply(m, rot);
    },

    scale(m, v) {
        const s = Mat4.identity();
        s[0] = v[0]; s[5] = v[1]; s[10] = v[2];
        return Mat4.multiply(m, s);
    },

    translate(m, v) {
        const t = Mat4.identity();
        t[12] = v[0]; t[13] = v[1]; t[14] = v[2];
        return Mat4.multiply(m, t);
    }
};

window.Mat4 = Mat4;
