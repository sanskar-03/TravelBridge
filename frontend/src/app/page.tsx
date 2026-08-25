import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-12">
      {/* Hero Section */}
      <section className="space-y-6 max-w-2xl">
        <h1 className="text-4xl font-bold text-primary tracking-tight">
          Send an item with someone already heading there.
        </h1>
        <p className="text-lg text-text-secondary leading-relaxed">
          Connect with travelers who have extra baggage space. A practical, peer-to-peer way to get your packages delivered safely.
        </p>
        <div className="flex items-center gap-4">
          <Button variant="primary" size="lg">Request a delivery</Button>
          <Button variant="outline" size="lg">Post your trip</Button>
        </div>
      </section>

      <hr className="border-border" />

      {/* Component Demo Section (Sample Data) */}
      <section className="space-y-8">
        <div>
          <h2 className="text-2xl font-semibold text-primary mb-2">Active Journeys (Sample)</h2>
          <p className="text-sm text-text-muted">Demonstrating Design System Components (Part 03)</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader className="flex flex-row justify-between items-start">
              <div>
                <CardTitle>London → New York</CardTitle>
                <p className="text-sm mt-1">Oct 24, 2026</p>
              </div>
              <Badge variant="success">Verified</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between text-sm">
                <span>Available Capacity:</span>
                <span className="font-medium text-text-primary">5 kg</span>
              </div>
              <Button variant="secondary" className="w-full">Message Traveler</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row justify-between items-start">
              <div>
                <CardTitle>Tokyo → Sydney</CardTitle>
                <p className="text-sm mt-1">Oct 28, 2026</p>
              </div>
              <Badge variant="info">Pending</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between text-sm">
                <span>Available Capacity:</span>
                <span className="font-medium text-text-primary">2 kg</span>
              </div>
              <Button variant="secondary" className="w-full">Message Traveler</Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
