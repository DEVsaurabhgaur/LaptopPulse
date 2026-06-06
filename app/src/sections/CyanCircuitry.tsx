import { useRef, useEffect, useMemo, useCallback } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface GridNode {
  x: number
  y: number
  z: number
  path: { x: number; y: number; z: number }[] | null
}

function createGrid(dimX: number, dimY: number, dimZ: number): GridNode[][][] {
  const grid: GridNode[][][] = []
  for (let x = 0; x < dimX; x++) {
    grid[x] = []
    for (let y = 0; y < dimY; y++) {
      grid[x][y] = []
      for (let z = 0; z < dimZ; z++) {
        grid[x][y][z] = { x, y, z, path: null }
      }
    }
  }

  const startNode = grid[0][0][0]
  const endNode = grid[dimX - 1][dimY - 1][dimZ - 1]
  let current = startNode
  current.path = []
  const dx = dimX - 1
  const dy = dimY - 1
  const dz = dimZ - 1
  const totalSteps = dx + dy + dz

  for (let i = 0; i < totalSteps; i++) {
    const canX = current.x < dimX - 1
    const canY = current.y < dimY - 1
    const canZ = current.z < dimZ - 1
    const sum = (canX ? 1 : 0) + (canY ? 1 : 0) + (canZ ? 1 : 0)
    const pick = Math.floor(Math.random() * sum)
    const options = ['x', 'y', 'z'].filter((_, idx) => {
      if (idx === 0) return canX
      if (idx === 1) return canY
      return canZ
    })
    const axis = options[pick]

    current.path!.push({ x: current.x, y: current.y, z: current.z })
    current = grid[
      current.x + (axis === 'x' ? 1 : 0)
    ][
      current.y + (axis === 'y' ? 1 : 0)
    ][
      current.z + (axis === 'z' ? 1 : 0)
    ]
    current.path = current.path || []
    current.path.push({ x: current.x, y: current.y, z: current.z })
  }

  current.path!.push({ x: endNode.x, y: endNode.y, z: endNode.z })
  endNode.path = current.path

  return grid
}

interface CircuitSceneProps {
  isDashboard?: boolean
}

function CircuitScene({ isDashboard = false }: CircuitSceneProps) {
  const groupRef = useRef<THREE.Group>(null)
  const mouseRef = useRef({ x: 0.5, y: 0.5, prevX: 0.5, prevY: 0.5 })
  const rotationRef = useRef({ x: 0, z: 0 })

  const spacing = isDashboard ? 2.5 : 3.0
  const dimX = isDashboard ? 5 : 8
  const dimY = isDashboard ? 4 : 6
  const dimZ = isDashboard ? 3 : 5
  const particleCount = isDashboard ? 500 : 1000

  const pathCurves = useMemo(() => {
    const g = createGrid(dimX, dimY, dimZ)
    const curves: THREE.CatmullRomCurve3[] = []

    for (let x = 0; x < dimX; x++) {
      for (let y = 0; y < dimY; y++) {
        for (let z = 0; z < dimZ; z++) {
          const node = g[x][y][z]
          if (node.path && node.path.length > 1) {
            const points = node.path.map(
              (p) => new THREE.Vector3(p.x * spacing, p.y * spacing, p.z * spacing)
            )
            curves.push(new THREE.CatmullRomCurve3(points))
          }
        }
      }
    }

    return curves
  }, [dimX, dimY, dimZ, spacing])

  const particlePositions = useMemo(() => {
    const positions: { x: number; y: number; z: number; color: string }[] = []
    for (let i = 0; i < particleCount; i++) {
      const gx = Math.floor(Math.random() * dimX)
      const gy = Math.floor(Math.random() * dimY)
      const gz = Math.floor(Math.random() * dimZ)
      const rnd = (Math.random() - 0.5) * 0.5
      const isCyan = Math.random() > 0.98
      positions.push({
        x: gx * spacing + rnd,
        y: gy * spacing + rnd,
        z: gz * spacing + rnd,
        color: isCyan ? '#00E5FF' : '#FFFFFF',
      })
    }
    return positions
  }, [dimX, dimY, dimZ, spacing, particleCount])

  const handlePointerMove = useCallback((e: THREE.Event & { clientX: number; clientY: number }) => {
    if (isDashboard) return
    const rect = (e.target as HTMLCanvasElement).getBoundingClientRect?.()
    if (!rect) return
    mouseRef.current.x = (e.clientX - rect.left) / rect.width
    mouseRef.current.y = (e.clientY - rect.top) / rect.height
  }, [isDashboard])

  useEffect(() => {
    if (!isDashboard) {
      const canvas = document.querySelector('canvas')
      if (canvas) {
        const onMove = (e: MouseEvent) => {
          const rect = canvas.getBoundingClientRect()
          mouseRef.current.x = (e.clientX - rect.left) / rect.width
          mouseRef.current.y = (e.clientY - rect.top) / rect.height
        }
        canvas.addEventListener('mousemove', onMove)
        return () => canvas.removeEventListener('mousemove', onMove)
      }
    }
  }, [isDashboard])

  useFrame((_, delta) => {
    if (!groupRef.current) return

    if (!isDashboard) {
      const mouseDelta =
        Math.abs(mouseRef.current.x - mouseRef.current.prevX) +
        Math.abs(mouseRef.current.y - mouseRef.current.prevY)

      if (mouseDelta < 0.001) {
        groupRef.current.rotation.z += delta * 0.05
      }

      const targetZ = (mouseRef.current.x - 0.5) * 0.5
      const targetX = (mouseRef.current.y - 0.5) * 0.5
      rotationRef.current.z += (targetZ - rotationRef.current.z) * 0.05
      rotationRef.current.x += (targetX - rotationRef.current.x) * 0.05
      groupRef.current.rotation.x = rotationRef.current.x

      mouseRef.current.prevX = mouseRef.current.x
      mouseRef.current.prevY = mouseRef.current.y
    } else {
      groupRef.current.rotation.z += delta * 0.1
    }
  })

  const centerOffset = useMemo(() => {
    return new THREE.Vector3(
      ((dimX - 1) * spacing) / 2,
      ((dimY - 1) * spacing) / 2,
      ((dimZ - 1) * spacing) / 2
    )
  }, [dimX, dimY, dimZ, spacing])

  return (
    <group ref={groupRef} onPointerMove={handlePointerMove as unknown as never} position={[-centerOffset.x, -centerOffset.y, -centerOffset.z]}>
      {/* Particles */}
      <instancedMesh args={[new THREE.SphereGeometry(0.1, 8, 8), new THREE.MeshBasicMaterial({ color: '#FFFFFF', transparent: true, opacity: 0.6, depthWrite: false }), particleCount]}>
        {particlePositions.map((pos, i) => {
          const dummy = new THREE.Object3D()
          dummy.position.set(pos.x, pos.y, pos.z)
          dummy.updateMatrix()
          return <primitive key={i} object={dummy.matrix} attach={`matrix-${i}`} />
        })}

      </instancedMesh>

      {/* Colored particles overlay */}
      {particlePositions.filter(p => p.color === '#00E5FF').map((pos, i) => (
        <mesh key={`cyan-${i}`} position={[pos.x, pos.y, pos.z]}>
          <sphereGeometry args={[0.1, 8, 8]} />
          <meshBasicMaterial color="#00E5FF" transparent opacity={0.6} depthWrite={false} />
        </mesh>
      ))}

      {/* Tubes */}
      {pathCurves.map((curve, i) => (
        <group key={`tube-${i}`}>
          <mesh>
            <tubeGeometry args={[curve, 64, 0.05, 4, false]} />
            <meshPhongMaterial color="#0A0A0A" shininess={100} specular={new THREE.Color('#444444')} />
          </mesh>
          {!isDashboard && Math.random() > 0.9 && (
            <mesh>
              <tubeGeometry args={[curve, 64, 0.06, 4, false]} />
              <meshPhongMaterial
                color="#0A0A0A"
                shininess={100}
                specular={new THREE.Color('#444444')}
                emissive={new THREE.Color('#00E5FF')}
                emissiveIntensity={0.3}
              />
            </mesh>
          )}
        </group>
      ))}
    </group>
  )
}

interface CyanCircuitryProps {
  className?: string
  isDashboard?: boolean
}

export default function CyanCircuitry({ className = '', isDashboard = false }: CyanCircuitryProps) {
  const cameraPosition: [number, number, number] = isDashboard ? [0, 0, 25] : [0, -20, 20]

  return (
    <div className={className} style={{ position: 'absolute', inset: 0 }}>
      <Canvas
        camera={{ position: cameraPosition, fov: isDashboard ? 45 : 50, near: 0.1, far: 1000 }}
        style={{ background: isDashboard ? 'transparent' : '#000000' }}
        gl={{ antialias: true, alpha: isDashboard }}
      >
        <hemisphereLight args={['#ffffff', '#444444', 0.6]} />
        <directionalLight position={[10, 10, 10]} color="#ffffff" intensity={0.5} castShadow />
        <CircuitScene isDashboard={isDashboard} />
      </Canvas>
    </div>
  )
}
