import { SignUp } from '@clerk/nextjs';

export default function RegisterPage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <h1
          style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: '#e2e8f0',
            marginBottom: '2rem',
            letterSpacing: '-0.025em',
          }}
        >
          NEXUS <span style={{ color: '#3b82f6' }}>V3</span>
        </h1>
        <SignUp
          appearance={{
            elements: {
              rootBox: {
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4)',
                borderRadius: '1rem',
              },
            },
          }}
        />
      </div>
    </div>
  );
}
