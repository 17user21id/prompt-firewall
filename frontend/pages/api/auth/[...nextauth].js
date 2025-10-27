import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

// Wrapper to disable caching
function NoCacheHandler(handler) {
  return async (req, res) => {
    res.setHeader('Cache-Control', 'no-store, max-age=0');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
    return handler(req, res);
  };
}

const nextAuthHandler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        name: { label: 'Tenant Name', type: 'text' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        try {
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tenants/login`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json' 
            },
            body: JSON.stringify({
              name: credentials.name,
              password: credentials.password,
            }),
          });

          const data = await res.json();
          
          if (res.ok && data.tenant_id) {
            return {
              id: data.tenant_id,
              name: data.name,
              tenant_id: data.tenant_id,
              api_key: data.api_key,
            };
          }
          
          return null;
        } catch (error) {
          console.error('Auth error:', error);
          return null;
        }
      },
    }),
  ],
  pages: {
    signIn: '/admin',
  },
  session: {
    strategy: 'jwt',
    maxAge: 24 * 60 * 60, // 24 hours
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.tenant_id = user.tenant_id;
        token.api_key = user.api_key;
        token.name = user.name;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.tenant_id = token.tenant_id;
      session.user.api_key = token.api_key;
      session.user.name = token.name;
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.NODE_ENV === 'development',
});

export default NoCacheHandler(nextAuthHandler);
